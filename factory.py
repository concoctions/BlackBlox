# -*- coding: utf-8 -*-
""" Factory class

This module contains the Factory class, which are objects that 
link together (and can generate) a set of product chains. One product chain
produces the primary product(s) of the factory, whereas other auxillary chains
provide inflows or processes outflows from the main chain or other auxillary
chains. Auxillary chains can be attached to any process in any chain in the
factory.

Module Outline:

- import statements and logger
- class: Factory
    - class function: Build
    - class function: Balance
    - class function: Diagram

"""

import pandas as pan
from math import isnan
from collections import defaultdict
from graphviz import Digraph
from datetime import datetime
from bb_log import get_logger
import io_functions as iof
import dataconfig as dat
import unitprocess as unit
import processchain as cha
import calculators as calc

logger = get_logger("Factory")

class Factory:
    """Factories are sets of one or more connected products chains

    Factories have a primary product chain, and are balanced on a specific
    outflow of that chain. Auxillary chains link to the main chain (or other
    auxillary chains) at any or multiple unit processes in the chain, and 
    balance on a specified inflow or outflow of that unit process(es), i.e.
    it is assumed the auxillary chain is either providing the inflow or
    accepting the outflow.

    Factories balance on a specified output product. Product chains that 
    are not the main output product balance on the relevent inputs and 
    outputs of the main product. All product chains in a factory are run 
    using variables from the same scenario.

    Note:
        The product chain (main chain) is assumed to be the first chain
        in the tabular data listing the chains in the factory.

    Args:
        chains_file (DataFrame/str): Dataframe or filepath to tabular data
            detailing the process chains in the factory. The chain in the first
            row of data is assumed to be the main product flow.
            Must contain columns for:
            [Chain Name, Chain Product, Product_IO, ChainFile]
        connections_file (DataFrame/str): Dataframe or filepath to tabular data 
            detailing the connections between the chains in the factory. 
            Must contain columns for:
            [OriginChain, OriginProcess, Product, Product_IO_of_Origin, 
            Product_IO_of_Destination, DestinationChain]    
        name (str, optional): The name of the factory. Defaults to False.

    Attributes:
        name (str): The name of the factory.
        chains_df (data frame): Tabular data of the factory chains and the
            location of their data.
        connections_df (data frame): Tabuloar data of the connections
            between the factory chains.
        main_chain (str): the name of the factory's product chain, taken from
            the first row of chains_df.
        main_product (str): the name of the factory's main product, taken from 
            the first row of chains_df.
        chain_dict (dict): Dictionary of dictionaries containing process chain 
            objects in the factory. Each chain name is an entry key, with a 
            value of a dictionary containing the process chain object, name,
            product, and whether that product is a chain inflow or outflow.  
    """

    def __init__(self, chain_list_file, connections_file=None, chain_list_sheet=None, 
                 connections_sheet=None, name="Factory"):
        self.name = name
        self.chains_file = chain_list_file
        self.chains_df = iof.make_df(chain_list_file, chain_list_sheet, index=None)
        if connections_file is None:
            if connections_sheet is None or connections_sheet in dat.no_var:
                self.connections_df = None
            self.connections_df = iof.make_df(chain_list_file, connections_sheet, index=None)
        elif connections_sheet is not None and connections_sheet not in dat.no_var:
            self.connections_df = iof.make_df(connections_file, connections_sheet, index=None)
        else:
            self.connections_df = None
        self.main_chain = False
        self.main_product = False
        self.chain_dict = False

    def build(self):
        """Generates the needed process chain objects for the factory

        Locates the data specified for each process chain, and generates
        objects for each chain. Populates self.main_chain, self.main_product,
        and self.chain_dict.

        """
        logger.debug(f"initializing factory for {self.name}")
        
        chain_dict = defaultdict(dict)

        for i, c in self.chains_df.iterrows():
            name = c[dat.chain_name] 
            if i == 0:
                self.main_chain = name
                self.main_product = c[dat.chain_product]
            
            chain_sheet = iof.check_for_col(self.chains_df, dat.chain_sheetname, i)

            if (dat.chain_filepath not in self.chains_df 
                or iof.clean_str(c[dat.chain_filepath]) in dat.same_xls):
                chain_file = self.chains_file
            else:
                chain_file = c[dat.chain_filepath]
                
            chain_dict[name] = dict(chain=cha.ProductChain(chain_file, 
                                    name=name, xls_sheet=chain_sheet), 
                                    name=name, 
                                    product=c[dat.chain_product], 
                                    i_o=iof.clean_str(c[dat.chain_io][0]))

            chain_dict[name]['chain'].build()

        self.chain_dict = chain_dict

    def balance(self, product_qty, product=False, product_unit=False, product_io=False, 
                scenario=dat.default_scenario,write_to_xls=True, outdir=dat.outdir, 
                mass_energy=True, energy_flows=dat.energy_flows):
        """Calculates the mass balance of the factory

        Based on a quantity of the factory's main product, calculates the 
        remaining quantities of all flows in the factory, assuming all unit 
        processes are well-specified with zero degrees of freedom.

        Args:
            product_qty (float): the quantity of the product to balance on.
            product (str/bool): the product name. If False, uses the default
                product in the chain object attributes.
                (Defaults to False)
            scenario (str): The name of the scenario of variable values to use, 
                corresponding to the matching row index in each unit process's
                var_df. 
                (Defaults to the string specified in dat.default_scenario)
            write_to_xls (bool): If True, outputs the balances to an excel 
                workbook, with sheets for factory totals, inflows and outflows
                for all unit processes, and inflows and outflows by chain.
                (Defaults to True)
            outdir (str): Filepath where to create the balance spreadsheets.
                (Defaults to the outdir specified in dataconfig)  
            mass_energy (bool): If true, seperates mass and energy flows within 
                each excel sheet, adding rows for the respective totals.
                (Defaults to True)
            energy_flows (list): list of prefix/suffixes used to identify which 
                substances are energy flows and seperates them.
                (Defaults to dat.energy_flows)

        Returns:
            dictionary of factory total inflow quantities by substance
            dictionary of factory total outflow quantities by substance

        """       
       
        if not self.chain_dict:
            self.build()

        logger.debug(f"\n\nattempting to balance factory on {product_qty} of {self.chain_dict[self.main_chain]['product']}")

        io_dicts = {
            'i': iof.nested_dicts(3, float), #io_dicts['i'][chain][unit][substance] = float
            'o': iof.nested_dicts(3, float), #io_dicts['o'][chain][unit][substance] = float
            }
        chain_intermediates_dict = iof.nested_dicts(3, float)
        intermediate_product_dict = defaultdict(float) #intra-factory flows (to be discarded from totals)
        remaining_product_dict = iof.nested_dicts(4, float) #keeps track if a product has been used for recycle already dict[i_o][chain][unit][substance] = float
        internal_flows = []
        main = self.chain_dict[self.main_chain]

        if product is False:
            product = main['product']
        
        # balances main chain
        (io_dicts['i'][main['name']], 
        io_dicts['o'][main['name']], 
        chain_intermediates_dict[main['name']], 
        main_chain_internal_flows) = main['chain'].balance(product_qty, 
                                                           product = product, 
                                                           i_o = product_io,
                                                           unit_process = product_unit,
                                                           scenario=scenario)

        internal_flows.extend(main_chain_internal_flows)

        # balances auxillary chains and recycle flows based on connections dataframe
        if self.connections_df is not None:
            for dummy_index, aux in self.connections_df.iterrows(): 
                qty = None
                orig_unit = False
                orig_product_io = iof.clean_str(aux[dat.origin_io][0])
                dest_product_io = iof.clean_str(aux[dat.dest_io][0])
                origin_product = aux[dat.origin_product]
                dest_unit = False
                dest_unit_name = False
                destination_product = False
                i_tmp = None
                o_tmp = None
                replace_flow = None
                purge = 0
                qty_remaining = 0
                max_replace_fraction = 1.0
                replace_fuel = False
                energy_replacing_fuel = False

                #gets origin and destination chain objects
                orig_chain = self.chain_dict[aux[dat.origin_chain]]['chain']
                if not io_dicts[orig_product_io][orig_chain.name]:
                    raise KeyError(f"{io_dicts[orig_product_io][orig_chain.name]} has not been balanced yet. Please check the order of your connections in your connections dataframe.")
                dest_chain = self.chain_dict[aux[dat.dest_chain]]['chain'] 
                if dat.dest_unit in aux:
                    if aux[dat.dest_unit] in dest_chain.process_dict:
                        dest_unit = dest_chain.process_dict[aux[dat.dest_unit]]
                        dest_unit_name = dest_unit.name

                if aux[dat.origin_unit] == dat.connect_all: #if connects to all, use totals from chain
                    qty = io_dicts[orig_product_io][orig_chain.name]['chain totals'][origin_product]
                    logger.debug(f"using {qty} of {origin_product} from all units in {orig_chain.name}")
                else:
                    orig_unit = orig_chain.process_dict[aux[dat.origin_unit]]
                    if product in remaining_product_dict[orig_product_io][orig_chain.name][orig_unit.name]: #check if some of the product has already been used for something
                        qty = remaining_product_dict[orig_product_io][orig_chain.name][orig_unit.name][product]
                        logger.debug(f"{origin_product} found in remaining_product_dict, {qty} unused.")
                    else:
                        qty = io_dicts[orig_product_io][orig_chain.name][orig_unit.name][product]
                        logger.debug(f"using {qty} of {origin_product} from {orig_unit.name} in {orig_chain.name}")

                if dat.purge_fraction in aux: 
                    if aux[dat.purge_fraction] not in dat.no_var:
                        if type(aux[dat.purge_fraction]) in [float, int] and not isnan(aux[dat.purge_fraction]):
                            calc.check_qty(aux[dat.purge_fraction], fraction=True)
                            purge = qty * aux[dat.purge_fraction]
                            qty = qty - purge
                            logger.debug(f"purge: {purge}, new qty: {qty}")
                
                if dat.max_replace_fraction in aux: # used for recycle flows only
                    if aux[dat.max_replace_fraction] not in dat.no_var:
                        if type(aux[dat.max_replace_fraction]) in [float, int] and not isnan(aux[dat.max_replace_fraction]):
                            calc.check_qty(aux[dat.max_replace_fraction], fraction=True)
                            max_replace_fraction = aux[dat.max_replace_fraction]
                
                # process recycle connections
                if dat.replace in aux and type(aux[dat.replace]) is str and aux[dat.replace] not in dat.no_var:
                    if aux[dat.replace] in unit.lookup_var_dict:
                        replace_flow = dest_unit.var_df.at[scenario, unit.lookup_var_dict[aux[dat.replace]]['lookup_var']] 
                        if aux[dat.replace] =='fuel':
                            replace_fuel = True
                    else: replace_flow = aux[dat.replace]
                    if replace_flow not in io_dicts[dest_product_io][dest_chain.name][dest_unit.name]:
                        raise ValueError(f"{replace_flow} not found in {dest_chain.name}'s {dest_unit.name} {dest_product_io}-flows")

                    r_kwargs = dict(original_inflows_dict=io_dicts['i'][dest_chain.name][dest_unit.name],
                                    original_outflows_dict=io_dicts['o'][dest_chain.name][dest_unit.name],
                                    recycled_qty=qty,
                                    recycle_io=dest_product_io,
                                    recycled_flow=origin_product,
                                    replaced_flow=replace_flow,
                                    max_replace_fraction=max_replace_fraction,
                                    scenario=scenario)

                    logger.debug(f"recycling {qty} of {origin_product} from {orig_unit.name} in {orig_chain.name} to replace {replace_flow} in {dest_unit.name} in {dest_chain.name}")
                    logger.debug("original IO Dicts:")
                    logger.debug(io_dicts['i'][dest_chain.name][dest_unit.name])
                    logger.debug(io_dicts['o'][dest_chain.name][dest_unit.name])
                    logger.debug(f"purge: {purge}, max replace fraction: {max_replace_fraction}")
                    logger.debug(f'replaces fuel{replace_fuel}')
                    if replace_fuel is True:
                        logger.debug(f"{product} replacing {replace_flow}")
                        for string in dat.energy_flows:
                            if product.startswith(string) or product.endswith(string):
                                logger.debug("replacing fuel with energy")
                                energy_replacing_fuel = True 
                                i_tmp, o_tmp, qty_remaining = dest_unit.recycle_energy_replacing_fuel(**r_kwargs)  
                                break

                    if energy_replacing_fuel is False:
                        i_tmp, o_tmp, qty_remaining = dest_unit.recycle_1to1(**r_kwargs)

                    logger.debug(f"sent {qty} of {origin_product} from {orig_unit.name} in {orig_chain.name} to replace {replace_flow} in {dest_unit.name} in {dest_chain.name} ")
                    io_dicts['i'][dest_chain.name][dest_unit.name].clear()
                    io_dicts['o'][dest_chain.name][dest_unit.name].clear()
                    io_dicts['i'][dest_chain.name][dest_unit.name] = i_tmp 
                    io_dicts['o'][dest_chain.name][dest_unit.name] = o_tmp 
                    logger.debug("replaced IO Dicts:")
                    logger.debug(io_dicts['i'][dest_chain.name][dest_unit.name])
                    logger.debug(io_dicts['o'][dest_chain.name][dest_unit.name])

                    # recalculate chain totals  
                    new_chain_totals = {
                        'i': defaultdict(float),
                        'o': defaultdict(float)
                        }

                    for process, inflows_dict in io_dicts['i'][dest_chain.name].items():
                        if process != 'chain totals':
                            for inflow, i_qty in inflows_dict.items():
                                new_chain_totals['i'][inflow] += i_qty
                    for process, outflows_dict in io_dicts['o'][dest_chain.name].items():
                        if process != 'chain totals':
                            for outflow, o_qty in outflows_dict.items():
                                new_chain_totals['o'][outflow] += o_qty
                    for io_dict in new_chain_totals:
                        for intermediate_product, int_qty in chain_intermediates_dict[dest_chain.name].items():
                            new_chain_totals[io_dict][intermediate_product] -= int_qty

                    io_dicts['i'][dest_chain.name]["chain totals"].clear()
                    io_dicts['o'][dest_chain.name]["chain totals"].clear()
                    io_dicts['i'][dest_chain.name]["chain totals"] = new_chain_totals['i']
                    io_dicts['o'][dest_chain.name]["chain totals"] = new_chain_totals['o']
                    remaining_product_dict[orig_product_io][orig_chain.name][orig_unit.name][origin_product] = qty_remaining
                    logger.debug(f"{remaining_product_dict[orig_product_io][orig_chain.name][orig_unit.name][origin_product]} {origin_product} remaining for {orig_chain.name}-{orig_unit.name}")


                # process non-reycle connection   
                else:         
                    if dat.dest_product in aux and type(aux[dat.dest_product]) is str and aux[dat.dest_product] not in dat.no_var:
                        destination_product = aux[dat.dest_product]
                    else:
                        destination_product = origin_product

                    logger.debug(f"sending {qty} of {origin_product } to {dest_chain.name} as {destination_product} ({dest_product_io}-flow)")
                    c_kwargs = dict(qty=qty, 
                                    product=destination_product, 
                                    i_o=dest_product_io, 
                                    unit_process = dest_unit_name,
                                    scenario=scenario,
                                    )
                    (i_tmp, 
                    o_tmp, 
                    chain_intermediates_dict[dest_chain.name],
                    chain_internal_flows) = dest_chain.balance(**c_kwargs)
                    internal_flows.extend(chain_internal_flows)
                
                    # add chain inflow/outflow data to factory inflow/outflow dictionaries
                    # check if the chain already exists, and if so, aggregate the flow values instead of assigning/replacing
                    if io_dicts['i'][dest_chain.name] and io_dicts['o'][dest_chain.name]:
                        for process_dict in i_tmp:
                            for substance, i_qty in i_tmp[process_dict].items():
                                io_dicts['i'][dest_chain.name][process_dict][substance] += i_qty
                        for process_dict in o_tmp:
                            for substance, o_qty in o_tmp[process_dict].items():
                                io_dicts['o'][dest_chain.name][process_dict][substance] += o_qty
                    else:    
                        io_dicts['i'][dest_chain.name] = i_tmp
                        io_dicts['o'][dest_chain.name] = o_tmp 
                    
                    logger.debug(f"{qty} of {origin_product} as product from {orig_chain.name} ({orig_product_io}) sent to to {dest_chain.name} ({dest_product_io})")

                intermediate_product_dict[origin_product] += (qty - qty_remaining)
                logger.debug(f"{qty - qty_remaining} of {origin_product} added to intermediate_product_dict")

                orig_chain_name = orig_chain.name
                dest_chain_name = dest_chain.name
                if orig_unit and orig_unit.name:
                    orig_unit_name = orig_unit.name
                elif aux[dat.origin_unit] == dat.connect_all:
                    orig_unit_name = 'all'
                else:
                    orig_unit_name = 'unknown'
                if dest_unit and dest_unit.name:
                    dest_unit_name = dest_unit.name
                elif dest_product_io == 'i':
                    dest_unit_name = dest_chain.process_names[0]
                elif dest_product_io == 'o':
                    dest_unit_name = dest_chain.process_names[-1]
                else:
                    dest_unit_name = 'unknown'

                if dest_product_io == 'o' and orig_product_io == 'i':
                    orig_chain_name, dest_chain_name = dest_chain_name, orig_chain_name
                    orig_unit_name, dest_unit_name = dest_unit_name, orig_unit_name

                internal_flows.append([orig_chain_name, orig_unit_name, f'{origin_product} as {destination_product}', (qty-qty_remaining), dest_chain_name, dest_unit_name])
    

        factory_totals = {
            'i': defaultdict(float),
            'o': defaultdict(float)
            }
        for chain in io_dicts['i']:
            for inflow, qty in io_dicts['i'][chain]['chain totals'].items():
                factory_totals['i'][inflow] += qty
        for chain in io_dicts['o']:
            for outflow, qty in io_dicts['o'][chain]['chain totals'].items():
                factory_totals['o'][outflow] += qty
        for io_dict in factory_totals:
            for product, qty in intermediate_product_dict.items():
                factory_totals[io_dict][product] -= qty # removes intermediate product quantities

        if write_to_xls is True:
            if outdir == dat.outdir:
                outdir = f'{dat.outdir}/{self.name}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'
                
            filename = f'f_{self.name}_{scenario}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

            meta_df = iof.metadata_df(user=dat.user_data, name=self.name, 
                          level="Factory", scenario=scenario, product=self.main_product,
                          product_qty=product_qty, energy_flows=energy_flows)

            totals_dict = iof.nested_dicts(2)
            totals_dict['factory inflows'] = factory_totals['i']
            totals_dict['factory outflows'] = factory_totals['o']
            totals_df = iof.make_df(totals_dict, drop_zero=True)
            totals_df = iof.mass_energy_df(totals_df)
            internal_flows_header = ['origin chain', 'origin unit', 'flow product', 'quantity', 'destination chain', 'destination unit']
            internal_flows_df = pan.DataFrame(internal_flows, columns=internal_flows_header)

            df_list = [meta_df, totals_df, internal_flows_df]
            sheet_list = ['metadata', f'{self.name} totals', 'internal flows']

            all_inflows = defaultdict(lambda: defaultdict(float))
            all_outflows = defaultdict(lambda: defaultdict(float))

            for chain in io_dicts['i']:
                columns = self.chain_dict[chain]['chain'].process_names + ['chain totals']
                chain_inflow_df = iof.make_df(io_dicts['i'][chain], 
                                              col_order=columns, 
                                              drop_zero=True)
                chain_inflow_df = iof.mass_energy_df(chain_inflow_df)
                df_list.append(chain_inflow_df)
                sheet_list.append(chain+" inflows")

                chain_outflow_df = iof.make_df(io_dicts['o'][chain], 
                                               col_order=columns,
                                               drop_zero=True)
                logger.debug(chain_outflow_df)
                chain_outflow_df = iof.mass_energy_df(chain_outflow_df)
                logger.debug(chain_outflow_df)
                df_list.append(chain_outflow_df)
                sheet_list.append(chain+" outflows")

                for process_dict in io_dicts['i'][chain]:
                    if 'total' not in process_dict:
                        for substance, qty in io_dicts['i'][chain][process_dict].items():
                            all_inflows[process_dict][substance] = qty
                        for substance, qty in io_dicts['o'][chain][process_dict].items():
                            all_outflows[process_dict][substance] = qty

            all_outflows_df = iof.make_df(all_outflows, drop_zero=True)
            all_outflows_df = iof.mass_energy_df(all_outflows_df, totals=False)
            df_list.insert(3,all_outflows_df)
            sheet_list.insert(3, "unit outflow matrix")

            all_inflows_df = iof.make_df(all_inflows, drop_zero=True)
            all_inflows_df = iof.mass_energy_df(all_inflows_df, totals=False)
            df_list.insert(3, all_inflows_df)
            sheet_list.insert(3, "unit inflow matrix")

            iof.write_to_excel(df_list, sheet_list=sheet_list, 
                               filedir=outdir, filename=filename)

        
        logger.debug(f"successfully balanced factory on {product_qty} of {self.chain_dict[self.main_chain]['product']}")

        return factory_totals['i'], factory_totals['o']


    def diagram(self, outdir=dat.outdir, view=False, save=True):
        """ Outputs a diagram of the factory flows to file.

        Using Graphviz, takes the unit process names, sets of inflows and 
        outflows, and the specified linkages of the factory to generate a
        diagram of the chain as a png and svg.
        
        Args:
            outdir(str): The output directory where to write the files.
                (Defaults to the output directory specified in dataconfig in
                a 'pfd' subfolder.)

            view(bool): If True, displays the diagram in the system
                viewer. 
                (Defaults to True)
        """

        if outdir == dat.outdir:
            outdir = f'{outdir}/{self.name}_{datetime.now().strftime("%Y-%m-%d_%H%M")}/pfd'

        if not self.chain_dict:
            self.build()
        
        filename = f'{self.name}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

        factory_diagram = Digraph(name="factory")
        factory_diagram.attr('node', shape='box', color='black')
        factory_diagrams = dict()
        io_diagram = Digraph(name=filename, directory=outdir, format='png',)
        io_diagram.attr('node', shape='box', color='white')
        

        # gets product chains
        for c in self.chain_dict:
            d_kwargs = dict(view=False,
                            outdir=f'{outdir}/{self.name}')
            diagram_dict = dict(diagram=self.chain_dict[c]['chain'].diagram(**d_kwargs),
                                process_list=self.chain_dict[c]['chain'].process_list, 
                                name=self.chain_dict[c]['name'], connect=[])
            if diagram_dict['name'] == self.main_chain:
                diagram_dict['diagram'].attr(rank='min')
            factory_diagrams[self.chain_dict[c]['name']] = diagram_dict

        # connects chains on factory intermediate products
        if self.connections_df is not None:
            for i, c in self.connections_df.iterrows():
                product = c[dat.origin_product]
                origin_chain = c[dat.origin_chain]
              # o_io = iof.clean_str(c[dat.origin_io][0])  # currently unused
                d_io = iof.clean_str(c[dat.dest_io][0])

            
                connection_color = 'blue'
                if d_io == 'i':
                    dest_chain = c[dat.dest_chain]+factory_diagrams[c[dat.dest_chain]]['process_list'][0]['process'].name
                elif d_io == 'o':
                    dest_chain = c[dat.dest_chain]+factory_diagrams[c[dat.dest_chain]]['process_list'][-1]['process'].name
                if dat.dest_unit in c: # if there's a destination unit, get the process index in the process list and them the name from the process
                    d_process_id_list = [u['process'].u_id for u in factory_diagrams[c[dat.dest_chain]]['process_list']]
                    if c[dat.dest_unit] in [u['process'].u_id for u in factory_diagrams[c[dat.dest_chain]]['process_list']]:
                        d_unit_index = d_process_id_list.index(c[dat.dest_unit])
                        dest_chain = c[dat.dest_chain]+factory_diagrams[c[dat.dest_chain]]['process_list'][d_unit_index]['process'].name
                        connection_color = 'green'

                if c[dat.origin_unit] == dat.connect_all:
                    origin_list = [c[dat.origin_chain]+p['process'].name for p in factory_diagrams[origin_chain]['process_list']]
                else:
                    o_process_id_list = [u['process'].u_id for u in factory_diagrams[c[dat.origin_chain]]['process_list']]
                    o_unit_index = o_process_id_list.index(c[dat.origin_unit])
                    origin_list = [c[dat.origin_chain]+factory_diagrams[c[dat.origin_chain]]['process_list'][o_unit_index]['process'].name]

                for origin in origin_list:
                    if d_io == 'i':
                        factory_diagram.edge(origin, dest_chain, label=product, color=connection_color, fontcolor=connection_color)
                    elif d_io == 'o':
                        factory_diagram.edge(dest_chain, origin, label=product, color=connection_color, fontcolor=connection_color)
                    

        # add inflows and outflows
        for d in factory_diagrams:
            chain = factory_diagrams[d]['name']
            diagram = factory_diagrams[d]['diagram']
            process_list = factory_diagrams[d]['process_list']
            for i, unit in enumerate(process_list):
                process = unit['process'].name
                inflows = '\n'.join(unit['process'].inflows)
                outflows = '\n'.join(unit['process'].outflows)

                if self.connections_df is not None:
                    for dummy_index, c in self.connections_df.iterrows():
                        if chain == c[dat.origin_chain]:
                            if process == c[dat.origin_unit] or c[dat.origin_unit] == dat.connect_all:
                                if iof.clean_str(c[dat.origin_io][0]) == 'i':
                                    inflows = inflows.replace(c[dat.origin_product], '')
                                if iof.clean_str(c[dat.origin_io][0]) == 'o':
                                    outflows = outflows.replace(c[dat.origin_product], '')
                            
                        if chain == c[dat.dest_chain]:
                            if iof.clean_str(c[dat.dest_io][0]) == 'i' and unit == process_list[0]:
                                inflows = inflows.replace(c[dat.origin_product], '')
                            if iof.clean_str(c[dat.dest_io][0]) == 'o' and unit == process_list[-1]:
                                outflows = outflows.replace(c[dat.origin_product], '')

                if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')

                if i == 0:
                    if inflows and not inflows.isspace():
                        io_diagram.node(chain+process+inflows, label=inflows)
                        factory_diagram.edge(chain+process+inflows, chain+process, color='black')

                    if len(process_list) == 1:
                        if outflows and not outflows.isspace():
                            io_diagram.node(chain+process+outflows, label=outflows)
                            factory_diagram.edge(chain+process, chain+process+outflows)

                    elif outflows != unit['o']:
                        outflows = outflows.replace(unit['o'], '')
                        if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                        if outflows and not outflows.isspace():
                            io_diagram.node(chain+process+outflows, label=outflows)
                            factory_diagram.edge(chain+process, chain+process+outflows)


                elif i < len(process_list) - 1:
                    if inflows != unit['i']:
                        inflows = inflows.replace(unit['i'], '')
                        if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                        if inflows and not inflows.isspace():
                            io_diagram.node(chain+process+inflows, label=inflows)
                            factory_diagram.edge(chain+process+inflows, chain+process)

                    if outflows != unit['o']:
                        outflows = outflows.replace(unit['o'], '')
                        if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                        if outflows and not outflows.isspace():
                            io_diagram.node(chain+process+outflows, label=outflows)
                            factory_diagram.edge(chain+process, chain+process+outflows)

                else:
                    if inflows != unit['i']:
                        inflows = inflows.replace(unit['i'], '')
                        if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                        if inflows and not inflows.isspace():
                            io_diagram.node(chain+process+inflows, label=inflows)
                            factory_diagram.edge(chain+process+inflows, chain+process)
                    
                    if outflows and not outflows.isspace():
                        io_diagram.node(chain+process+outflows, label=outflows)
                        factory_diagram.edge(chain+process, chain+process+outflows)


        i = 0
        for diagram in factory_diagrams:
            factory_diagrams[diagram]['diagram'].attr('graph', name='cluster'+str(i))
            factory_diagram.subgraph(factory_diagrams[diagram]['diagram'])
        i += 1

        io_diagram.subgraph(factory_diagram)

        io_diagram.engine = 'circo'
        
        if view is True:
            io_diagram.view()

        if save is True:
            io_diagram.render()
            io_diagram.format = 'svg'
            io_diagram.render()

        logger.debug(f"created diagram for {self.name} factory")