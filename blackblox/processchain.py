# -*- coding: utf-8 -*-
""" Chain class

This module contains the Product Chain class, which are objects that 
link together (and can generate) a linear sequence of unit processes.

Product chains can currently be balanced on an inflow of their initial
unit process or an outflow of their final unit process. It is also possible
to automatically generate diagrams of the flows in a product chain.

Module Outline:

- import statements and logger
- class: ProductChain
    - class function: Build
    - class function: Balance
    - class function: Diagram

"""

from collections import defaultdict
from datetime import datetime
from graphviz import Digraph
import pandas as pan

from blackblox.bb_log import get_logger

import blackblox.io_functions as iof
import blackblox.dataconfig as dat
import blackblox.unitprocess as unit
from blackblox.frames import df_unit_library


logger = get_logger("Chain")


class ProductChain:
    """Linear chain of connected unit processes.

    A ProductChain contains multiple unit processes that can be balanced via linear links:
    an outflow of one unit process is an inflow in the next unit process in the chain.
    
    Currently equires the use of df_unit_library

    Args:
        chain_data (dataframe/str): Dataframe or filepath to tabular data that 
            specifies the linkages of the unit process.
        name (str): Name for the chain. Optional.
            (Defaults to "Product Chain.)
        xls_sheet (str/None): Excel sheetname for chain data. Optional.
            (Defaults to None)

    Attributes:
        name: the name of the chain
        process_chain_df: the dataframe of chain linkages
        default_product: if no other product is specified when balancing
            the chain, this will be used. Determined by process_chain_df:
            if there is an outflow specified for the last process or an
            inflow specified for the first process. If both are specified,
            the outflow is used by default.
        process_list: list of unit process information generated using the
            process_chain_df.  The list is in order of the unit processes in 
            the chain, and each list item is a dictionary including the keys:
            - process: UnitProcess object
            - i: (str) inflow from process_chain_df
            - o: (str) inflow from process_chain_df

    """

    def __init__(self, chain_data, name="Product Chain", xls_sheet=None, outdir=None,
                 units_df=df_unit_library, units_df_basedir=dat.unit_process_library_file.parent):
        self.name = name
        self.outdir = outdir if outdir else dat.path_outdir / f'{dat.timestamp_str}__chain_{self.name}'

        logger.info(f"PROCESS CHAIN INIT - chain name: {name}, chain data: {chain_data}, xls sheet: {xls_sheet}")
        self.process_chain_df = iof.make_df(chain_data, sheet=xls_sheet, index=None)
        self.default_product = False
        self.process_list = []  # list of UnitProcess objects, in order (used in Factory balance)
        self.process_names = []  # list of UnitProcess names, in order
        self.process_ids = []  # list of UnitProcess unique IDs, in order
        self.process_dict = dict()  # keys: unit process IDs, values: unit process objects. (used in Factory balance)

        # create UnitProcess objects for each unit in chain
        for index, process_row in self.process_chain_df.iterrows():
            process = unit.UnitProcess(process_row[dat.process_col], units_df=units_df, units_df_basedir=units_df_basedir)
            logger.debug(f"{self.name.upper()}: UnitProcess object created for {process.name}")
            inflow = process_row[dat.inflow_col]
            outflow = process_row[dat.outflow_col]

            if inflow not in process.inflows and index != 0:
                raise KeyError(f"{inflow} not found in {process.name} inflows")           
            if (outflow not in process.outflows 
                and index !=self.process_chain_df.index[-1]):
                raise KeyError(f"{outflow} not found in {process.name} outflows")
 
            self.process_list.append(dict(process=process, i=inflow, o=outflow))
            self.process_ids.append(process.u_id)
            self.process_names.append(process.name)
            self.process_dict[process.u_id] = process
            
        # set deafult product
        if not self.default_product:
            if self.process_list[-1]['o'] in self.process_list[-1]['process'].outflows:
                self.default_product = self.process_list[-1]['o']
            elif self.process_list[0]['i'] in self.process_list[0]['process'].inflows:
                self.default_product = self.process_list[-1]['i']
            else:
                logger.debug(f"{self.name.upper()}: No default product found for {self.name}.")

    
    def balance(self, qty=1.0, product=False, i_o=False, unit_process=False, 
                product_alt_name=False, scenario=dat.default_scenario,
                write_to_console=False, write_to_xls = False):
        """balance(self, qty, product=False, i_o=False, scenario=dat.default_scenario)
        Calculates the mass balance of the product chain

        Based on a quantity of an inflow for the first unit process in the 
        chain or an outflow for the last unit process, calculates the remaining
        quantities of all flows in the chain, assuming all unit processes
        are well-specified with zero degrees of freedom.

        Args:
            qty (float): the quantity of the product to balance on.
            product (str/bool): the product name, as it appears in the chain. 
                If False, attepmts to use the default product in the chain object attributes.
                (Defaults to False)
            i_o (str/bool): "i" or "o" indicating whether the product is an inflow
                or outflow. 
                If False, attempts to assign based on chain inflows
                and outflows.
                (Defaults to False)
            unit_process (str): Name of the unit process where the product exists.
                Required if the unit process does not begin or end a chain.
                (Default to False)
            product_alt_name (str): Product name as it appears in linked unit 
                process, if different than in unit process to be balanced
                (e.g. "blast furnace gas" exiting a blast furnace process would be
                product_alt_name for the "waste heat" product entering "coke oven")
            scenario (str): The var_df index identifier of the set of variables 
                values to use when balancing Unit Processes.
                (Defaults to the string specified in dat.default_scenario)

        Returns:
            - 3-level nested dictionary of inflows, ``[unit process][flowtype][substance] = (float)``
            - 3-level nested dictionary of outflows, ``[unit process][flowtype][substance] = (float)``
            - dictionary of intermediate flows, ``[substance] = (float)``
            - list of lists of internal flows, ``[chain, origin unit, product, qty (float), chain, destination unit]``

        """

        chain = self.process_list.copy() # to avoid manipulating self.process_list directly
        product_qty = qty

        # identify UnitProcess of balancing product (start) and divides chains into processes
        # before the start process (upstream) and after the start process (downstream)
        if unit_process is not False:
            logger.debug(f"{self.name.upper()}: attempting to balance chain at {unit_process}")
            if unit_process in self.process_ids:
                unit_index = self.process_ids.index(unit_process)
                upstream = chain[0:unit_index]
                upstream.reverse()
                downstream = chain[unit_index+1:]
                start = chain[unit_index]['process']
            else:
                raise KeyError(f"{unit_process} not found in {self.name} process list")

            if product is False:
                raise ValueError(f"If specifying a unit process, product cannot be False")

            if i_o is False:
                raise ValueError(f"If specifying a unit process, i_o cannot be False")
            else:
                i_o = iof.clean_str(i_o[0])
                if i_o not in ['i', 'o']:
                    raise ValueError("i_o must start with 'i' for inflow or 'o' for outflow")

            if i_o == 'i':
                if product not in chain[unit_index]['process'].inflows:
                    raise KeyError(f"{product} is not an {i_o}-flow of {start.name}")
            else:
                if product not in chain[unit_index]['process'].outflows:
                    raise KeyError(f"{product} is not an {i_o}-flow of {start.name}")
       
        else:
            if product is False:
                product = self.default_product
            logger.debug(f"{self.name.upper()}: attempting to balance chain on {product}")

            if i_o:
                i_o = iof.clean_str(i_o[0]) 

            if product in chain[-1]['process'].outflows and i_o != 'i':
                start = chain[-1]['process']
                chain.reverse()
                upstream = chain[1:]
                downstream = False
                i_o = 'o'
            elif product in chain[0]['process'].inflows and i_o != 'o':
                start = chain[0]['process']
                upstream = False
                downstream = chain[1:]
                i_o = 'i'
            else:
                raise KeyError(f"{product} not found as input or outflow of chain.")

        # create dictionaries of chain inflows, outflows, and flows between chain UnitProcesses
        io_dicts = {
            'i': defaultdict(lambda: defaultdict(float)), 
            'o': defaultdict(lambda: defaultdict(float))
            }
        intermediate_product_dict = defaultdict(float)
        internal_flows = []

        orig_product = product
        # balances starting process
        logger.debug(f"{self.name.upper()}: attempting to balance {start.name} on {qty} of {product}({i_o}) using {scenario} variables.")
        (io_dicts['i'][start.name], io_dicts['o'][start.name]) = start.balance(qty, product, i_o, scenario, product_alt_name=product_alt_name)
 
        # balances individual UnitProcesses in order
        for stream, prod_io, qty_io in [(upstream,'o', 'i'),(downstream, 'i', 'o')]:
            if stream is not False:
                for i, unit in enumerate(stream):
                    process = unit['process']

                    if i == 0:
                        previous_process = start

                    product = unit[prod_io]
                    qty = io_dicts[qty_io][previous_process.name][product]
                    intermediate_product_dict[product] = qty
                    internal_flows.append([self.name, previous_process.name, product, qty, self.name, process.name])

                    logger.debug(f"{self.name.upper()}: attempting to balance {process.name} on {qty} of {product}({prod_io}) using {scenario} variables.")
                    (io_dicts['i'][process.name], 
                    io_dicts['o'][process.name]) = process.balance(qty, product, prod_io, scenario)

                    previous_process = process

        totals = {
            'i': defaultdict(float),
            'o': defaultdict(float)
            }

        # aggregates inflows and outflows from all unit processes
        for dummy_process, inflows_dict in io_dicts['i'].items():
            for inflow, qty in inflows_dict.items():
                totals['i'][inflow] += qty
        
        for dummy_process, outflows_dict in io_dicts['o'].items():
            for outflow, qty in outflows_dict.items():
                totals['o'][outflow] += qty

        # removes intra-chain flows
        for io_dict in totals:
            for product, qty in intermediate_product_dict.items():
                totals[io_dict][product] -= qty

        # adds to inflow/outflow dictionaries
        io_dicts['i']["chain totals"] = totals['i']
        io_dicts['o']["chain totals"] = totals['o']
        
        logger.debug(f"{self.name.upper()}: successfully balanced {self.name} using {scenario} variables.")

        if write_to_console or write_to_xls is True:
            inflows_df = iof.mass_energy_df(io_dicts['i'])
            outflows_df = iof.mass_energy_df(io_dicts['o'])

        if write_to_console is True:
            print(f'\n{self.name.upper()}: balanced on {product_qty} of {orig_product} using {scenario} values')
            print("\ninflows:\n", inflows_df)
            print("\noutflows:\n", outflows_df)

            print("\nflows between Unit Processes")
            for row in internal_flows:
                print(row)

        if write_to_xls is True:
            internal_flows_header = ['origin unit', 'flow product', 'quantity', 'destination unit']
            for i in internal_flows:
                i.pop(4)
                i.pop(0)
            internal_flows_df = pan.DataFrame(internal_flows, columns=internal_flows_header)

            meta_df = iof.metadata_df(user=dat.user_data, 
                                        name=self.name, 
                                        level="Chain", 
                                        scenario=scenario, 
                                        product=product,
                                        product_qty=qty)

            dfs = [meta_df, inflows_df, outflows_df, internal_flows_df]
            sheets = ["meta", "inflows", "outflows", "internal_flows"]

            iof.write_to_xls(df_or_df_list=dfs,
                             sheet_list=sheets,
                             outdir=self.outdir,
                             filename=f'{self.name}_c_{scenario}_{dat.timestamp_str}')
                
        return io_dicts['i'], io_dicts['o'], intermediate_product_dict, internal_flows

    def run_scenarios(self, scenario_list=[], qty=1.0, product=False, i_o=False, product_alt_name=False, 
                      balance_energy=True, raise_imbalance=False, write_to_xls=True, write_to_console=False,
                      outdir=None):
        """Runs UnitProcess.balance over multiple scenarions of varaibles. Outputs to Excel.

        """
        
        iof.check_type(scenario_list, is_type=[list], not_not=True)
        scenario_dict = iof.nested_dicts(3)
        chain_dfs = []
        chain_sheets = []

        if product is False:
            product = self.default_product
        
        # balance UnitProcess on each scenario of variable values
        for scenario in scenario_list:
            c_in, c_out, dummy_intermediates, internal_flows = self.balance(qty=qty, 
                                               product=product,
                                               scenario=scenario,
                                               i_o=i_o,
                                               product_alt_name=product_alt_name,
                                               write_to_console=write_to_console)
            
            scenario_dict['i'][scenario] = c_in['chain totals']
            scenario_dict['o'][scenario] = c_out['chain totals']

            chain_dfs.extend([iof.mass_energy_df(c_in), iof.mass_energy_df(c_out)])
            chain_sheets.extend([f"IN - {scenario}", f"OUT - {scenario}"])

        if write_to_xls is True or write_to_console is True:
            inflows_df = iof.mass_energy_df(scenario_dict['i'])
            outflows_df = iof.mass_energy_df(scenario_dict['o'])

        if write_to_xls is True:
            internal_flows_header = ['origin unit', 'flow product', 'quantity', 'destination unit']
            for i in internal_flows:
                i.pop(4)
                i.pop(0)
            internal_flows_df = pan.DataFrame(internal_flows, columns=internal_flows_header)

            meta_df = iof.metadata_df(user=dat.user_data, 
                                        name=self.name, 
                                        level="Chain", 
                                        scenario=" ,".join(scenario_list), 
                                        product=product,
                                        product_qty=qty)

            dfs = [meta_df, inflows_df, outflows_df, internal_flows_df]
            sheets = ["meta", "IN - multi", "OUT - multi", "internal_flows"]
            dfs.extend(chain_dfs)
            sheets.extend(chain_sheets)

            outdir = outdir if outdir else self.outdir

            iof.write_to_xls(df_or_df_list=dfs,
                             sheet_list=sheets,
                             outdir=outdir,
                             filename=f'{self.name}_c_multi_{dat.timestamp_str}')

        if write_to_console is True:
            print(f"\n{str.upper(self.name)} balanced on {qty} of {product} for scenarios of {scenario_list}.\n")
            print("\nINFLOWS\n", inflows_df)
            print("\nOUTFLOWS\n", outflows_df, "\n")
        
        return inflows_df, outflows_df

    def diagram(self, view=True, save=True, outdir=False):
        """diagram(self, view_diagram=True, save=True, outdir=f'{dat.outdir}/pfd')
        Generates chain flow diagrams (png and svg) using Graphviz
        
        The use of a product flow subgraph allows the unconnected inflows and
        outflows to appear in invisible (white) nodes.

        Args:
            view(bool): If True, displays the diagram in the system
                viewer. 
                (Defaults to True)
            save (bool): If True, writes the diagram to file
                (Defaults to True)
            outdir(str/bool): The output directory where to write the files.
                (Defaults to the output directory specified in dataconfig in
                a 'pfd' subfolder.)

        Returns:
            The Digraph object of the product flow diagram, with each
            unit process as a node, with the concatanated chain name and 
            unit process name (e.g. chainunitprocess) as the identifier,
            and also the non-linking inflows and outflows as white-bordered
            nodes with concatanated chain, process, and flowtype (e.g.
            chainunitprocessinflows)
        """

        c = self.name  # used for building identifiers
        outdir = outdir if outdir else self.outdir
        filename = f'{c}_{datetime.now().strftime("%b%d_%H%M")}'

        chain_diagram = Digraph(name=filename, directory=outdir, format='png')
        product_flow = Digraph('mainflow_'+self.name)
        product_flow.graph_attr.update(rank='same')
        product_flow.attr('node', shape='box')
        chain_diagram.attr('node', shape='box')

        for i, unit in enumerate(self.process_list):
            name = unit['process'].name
            inflows = iof.clean_str('\n'.join(unit['process'].inflows))
            outflows = iof.clean_str('\n'.join(unit['process'].outflows))
            product_flow.node(c+name, label=name)

            # default line styling
            connection_color = dat.mass_color
            line_style = dat.mass_style


            if i == 0: # for first UnitProcess in chain
                if outflows != unit['o']:
                    outflows = iof.clean_str(outflows, str_to_cut=unit['o'], cut_whole_line_only=True)

            elif i < len(self.process_list) - 1: # for intermediate UnitProcesses
                
                # line styling if energy flow
                if iof.is_energy(unit['i']):
                    connection_color = dat.energy_color
                    line_style = dat.energy_style

                product_flow.edge(c+prevunit, c+name, label=unit['i'], color=connection_color, fontcolor=connection_color, style=line_style)

                if inflows != unit['i']:
                    inflows = iof.clean_str(inflows, str_to_cut=unit['i'], cut_whole_line_only=True)

                if outflows != unit['o']:
                    outflows = iof.clean_str(outflows, str_to_cut=unit['o'], cut_whole_line_only=True)

            else: # for last UnitProcess
                product_flow.edge(c+prevunit, c+name, label=unit['i'])

                if inflows != unit['i']:
                    inflows = iof.clean_str(inflows, str_to_cut=unit['i'], cut_whole_line_only=True)
                    
            chain_diagram.node(c+name+inflows, label=inflows, color='white')
            chain_diagram.edge(c+name+inflows, c+name)

            chain_diagram.node(c+name+outflows, label=outflows, color='white')
            chain_diagram.edge(c+name, c+name+outflows)

            prevunit = name

        chain_diagram.subgraph(product_flow)   

        if save is True:     # outputs as png and svg
            chain_diagram.render()
            chain_diagram.format = 'svg' 
            chain_diagram.render()

        if view is True:    # sends to system viewer
            chain_diagram.view()

        logger.debug(f"diagram created for {self.name} chain")
        return product_flow
