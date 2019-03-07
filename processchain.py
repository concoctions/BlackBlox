# -*- coding: utf-8 -*-
""" Product Chain class

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
from bb_log import get_logger
import io_functions as iof
import dataconfig as dat
import unitprocess as unit


logger = get_logger("Chain")


class ProductChain:
    """Linear linkage of unit processes.

    Product chains are a linear sets of unit process linked by their inflows
    and outflow; the outflow of a unit process must be an inflow into 
    the next unit process. Requires the existence of a unit process library
    file.

    Args:
        chain_data (dataframe/str): Dataframe or filepath to a excel or 
            tabular data that specifies the linkages of the unit process, 
            with each row detailing an inflow, a unit process, and an outflow,
            with the outflow in one row being the inflow in the next row.
            Chain data is order depedent. Specifying the inflow of the 
            first row or outflow of the last row is optional.
        name (str): Name for the chain. Optional.
            (Defaults to "Product Chain.)
        xls_sheet (str/None): Excel sheet where chain data resides. Optional.
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

    def __init__(self, chain_data, name="Product Chain", xls_sheet=None,):
        self.name = name
        self.process_chain_df = iof.make_df(chain_data, 
                                            sheet=xls_sheet, 
                                            index=None)
        self.default_product = False
        self.process_list = False
        self.process_names = False
        self.process_dict = False
    
    def build(self):
        """Generates the needed unit process objects

        Chekcs that the processes specified in the chain dataframe have 
        data available in the unit process library. Checks that the
        inflow and outflow specified in the chain exist for the associated
        unit process. Populates self.default_product and self.process_list.

        """
        logger.debug(f"initializing chain for {self.name}")
        process_list = []
        process_names = []
        process_dict = dict()

        for index, process_row in self.process_chain_df.iterrows():
            process = unit.UnitProcess(process_row[dat.process_col])
            inflow = process_row[dat.inflow_col]
            outflow = process_row[dat.outflow_col]

            if inflow not in process.inflows and index != 0:
                raise KeyError(f"{inflow} not found in {process.name} inflows")            
            
            if (outflow not in process.outflows 
                and index !=self.process_chain_df.index[-1]):
                raise KeyError(f"{outflow} not found in {process.name} outflows")
 
            process_list.append(dict(process=process, i=inflow, o=outflow))
            process_names.append(process.name)
            process_dict[process.name] = process
            
        self.process_list = process_list
        self.process_names = process_names
        self.process_dict = process_dict

        if not self.default_product:
            if process_list[-1]['o'] in process_list[-1]['process'].outflows:
                self.default_product = process_list[-1]['o']

            elif process_list[0]['i'] in process_list[0]['process'].inflows:
                self.default_product = process_list[-1]['i']

            else:
                logger.debug(f"No default product found for {self.name}.")

    
    def balance(self, qty, product=False, i_o=False, scenario=dat.default_scenario):
        """Calculates the mass balance of the product chain

        Based on a quantity of an inflow for the first unit process in the 
        chain or an outflow for the last unit process, calculates the remaining
        quantities of all flows in the chain, assuming all unit processes
        are well-specified with zero degrees of freedom.

        Args:
            qty (float): the quantity of the product to balance on
            product (str/bool): the product name. If False, uses the default
                product in the chain object attributes.
                (Defaults to False)
            i_o (str/bool): String beginning with "i" or "o". "i" if the product
                is an inflow of the chain's first unit process, "o" if it is an
                outflow of the chain's last unit process. If False, first checks
                to see if product exist in last unit process's outflows, then
                first unit process's inflows, and uses the first matching 
                product that it finds.
                (Defaults to False)
            scenario (str): The name of the scenario of variable values to use, 
                corresponding to the matching row index in each unit process's
                var_df. 
                (Defaults to the string specified in dat.default_scenario)

        Returns:
            3-level nested dictionary of inflows
            3-level nested dictionary of outflows
                each dictionary has the structure:
                [unit process][flowtype][substance] = quantity
            dictionary of intermediate flows, with the structure:
                [substance] = quanity
            list of lists of internal flows, with the item structure:
                [chain, origin unit, product, qty, chain, destination unit]
                everything besides qty is a string

        """

        if not self.process_list:
            self.build()

        chain = self.process_list.copy()

        if not product:
            product = self.default_product

        if i_o:
            i_o = iof.clean_str(i_o[0]) 
        if product in chain[-1]['process'].outflows and i_o != 'i':
            chain.reverse()
            i_o, io_opposite = 'o', 'i'
            io_opposite = 'i'
        elif product in chain[0]['process'].inflows and i_o != 'o':
            i_o, io_opposite = 'i', 'o'
        else:
            raise KeyError(f"{product} not found as input or outflow of chain.")

        io_dicts = {
            'i': defaultdict(lambda: defaultdict(float)), 
            'o': defaultdict(lambda: defaultdict(float))
            }
        intermediate_product_dict = defaultdict(float)
        internal_flows = []

        for i, unit in enumerate(chain):
            process = unit['process']

            if i != 0:
                product = unit[i_o]
                qty = io_dicts[io_opposite][previous_process.name][product]
                intermediate_product_dict[product] = qty
                internal_flows.append([self.name, previous_process.name, product, qty, self.name, process.name])

            logger.debug(f"attempting to balance {process.name} on {qty} of {product}({i_o}) using {scenario} variables.")
            (io_dicts['i'][process.name], 
             io_dicts['o'][process.name]) = process.balance(qty, product, i_o, scenario)

            previous_process = process

            
        totals = {
            'i': defaultdict(float),
            'o': defaultdict(float)
            }
        for dummy_process, inflows_dict in io_dicts['i'].items():
            for inflow, qty in inflows_dict.items():
                totals['i'][inflow] += qty
        for dummy_process, outflows_dict in io_dicts['o'].items():
            for outflow, qty in outflows_dict.items():
                totals['o'][outflow] += qty
        for io_dict in totals:
            for product, qty in intermediate_product_dict.items():
                totals[io_dict][product] -= qty
        io_dicts['i']["chain totals"] = totals['i']
        io_dicts['o']["chain totals"] = totals['o']
        

        logger.debug(f"successfully balanced {self.name} using {scenario} variables.")
        return io_dicts['i'], io_dicts['o'], intermediate_product_dict, internal_flows


    def diagram(self, view_diagram=True, outdir=f'{dat.outdir}/pfd'):
        """Generates a diagram of the chain

        Using Graphviz, takes the unit process names, sets of inflows and 
        outflows, and the specified linkages of the chain to generate a
        diagram of the chain as a png and svg.

        Code looks repetitive, but slightly different elements are needed to
        be generated if the unit process is the first in the list, a middle
        process, or the last unit process in the list, as well as a special
        case needed if the chain is only one unit process long. Each node is
        also given a long unique identifier, which is necessary for building
        factory-level diagrams.
        
        The use of a product flow subgraph allows the unconnected inflows and
        outflows to appear in invisible (white) nodes, and also is returnable
        for use in larger factory diagrams.

        Args:
            view_diagram(bool): If True, displays the diagram in the system
                viewer. 
                (Defaults to True)
            outdir(str): The output directory where to write the files.
                (Defaults to the output directory specified in dataconfig in
                a 'pfd' subfolder.)

        Returns:
            Optional: The Digraph object of the product flow diagram, with each
            unit process as a node, with the concatanated chain name and 
            unit process name (e.g. chainunitprocess) as the identifier,
            and also the non-linking inflows and outflows as white-bordered
            nodes with concatanated chain, process, and flowtype (e.g.
            chainunitprocessinflows)

        """

        if not self.process_list:
            self.build()        

        c = self.name

        filename = f'{c}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

        chain_diagram = Digraph(name=filename, directory=outdir, format='png')
        product_flow = Digraph('mainflow_'+self.name)
        product_flow.graph_attr.update(rank='same')
        product_flow.attr('node', shape='box')
        chain_diagram.attr('node', shape='box')

        for i, unit in enumerate(self.process_list):
            name = unit['process'].name
            inflows = '\n'.join(unit['process'].inflows)
            outflows = '\n'.join(unit['process'].outflows)
            product_flow.node(c+name, label=name)

            if i == 0:
                chain_diagram.node(c+name+inflows, label=inflows, color='white')
                chain_diagram.edge(c+name+inflows, c+name)

                if len(self.process_list) == 1: 
                    chain_diagram.node(c+name+outflows, label=outflows, color='white')
                    chain_diagram.edge(c+name, c+name+outflows)

                elif outflows != unit['o']:
                    outflows = iof.clean_str(outflows, str_to_cut=unit['o'])
                    chain_diagram.node(c+name+outflows, label=outflows, color='white')
                    chain_diagram.edge(c+name, c+name+outflows)

            elif i < len(self.process_list) - 1:
                product_flow.edge(c+prevunit, c+name, label=unit['i'])

                if inflows != unit['i']:
                    inflows = iof.clean_str(inflows, str_to_cut=unit['i'])
                    chain_diagram.node(c+name+inflows, label=inflows, color='white')
                    chain_diagram.edge(c+name+inflows, c+name)

                if outflows != unit['o']:
                    outflows = iof.clean_str(outflows, str_to_cut=unit['o'])
                    chain_diagram.node(c+name+outflows, label=outflows, color='white')
                    chain_diagram.edge(c+name, c+name+outflows)

            else:
                product_flow.edge(c+prevunit, c+name, label=unit['i'])

                if inflows != unit['i']:
                    inflows = iof.clean_str(inflows, str_to_cut=unit['i'])
                    chain_diagram.node(c+name+inflows, label=inflows, color='white')
                    chain_diagram.edge(c+name+inflows, c+name)

                chain_diagram.node(c+name+outflows, label=outflows, color='white')
                chain_diagram.edge(c+name, c+name+outflows)

            prevunit = name

        chain_diagram.subgraph(product_flow)        
        chain_diagram.render()
        chain_diagram.format = 'svg'
        chain_diagram.render()

        if view_diagram:
            chain_diagram.view()

        logger.debug(f"diagram created for {self.name} chain")
        return product_flow
