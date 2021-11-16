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
    - class function: Balance
    - class function: Diagram
    - class function: Run_Scenarios
    
    used in factory.Balance():
    - class subfunction: check_origin_product
    - class subfunction: check_product_qty
    - class subfunction: check_for_value
    - class subfunction: check_for_recycle_fractions
    - class subfunction: check_for_lookup
    - class subfunction: connect_recycle_flow
    - class subfunction: update_chain_dict_after_recycle
    - class subfunction: describe_internal_flow
    - class subfunction: add_updownstream_flows
    - class subfunction: factory_to_excel
"""
# Graphviz does not want to go on my PATH on my work desktop, thus...
import platform
from collections import defaultdict
from math import isnan

import pandas as pan
from graphviz import Digraph

import blackblox.calculators as calc
import blackblox.dataconfig as dat
import blackblox.io_functions as iof
import blackblox.processchain as cha
import blackblox.unitprocess as unit
from blackblox.bb_log import get_logger
from blackblox.frames import (df_upstream_outflows, df_upstream_inflows, df_downstream_outflows, df_downstream_inflows,
                              df_unit_library)
from blackblox.unitprocess import lookup_var_dict


if platform.system() == 'Windows':
    import os
    os.environ["PATH"] += os.pathsep + dat.graphviz_path

logger = get_logger("Factory")


class Factory:
    """Factories link together multiple ProductChains.

    A Factory has a main ProductChain, which contains their default outflow
    product. One or more auxillary chains (of one or more unit processes) can
    be linked to the main ProductChain at any product of any UnitProcess in the 
    main ProductChain. Auxillary chains can also link to other auxillary chains.

    All UnitProcesses in a factory are balanced using variables from their 
    respective var_dr, with the same scenario identifier required for all. 

    Args:
        chains_list_file (DataFrame/str): Dataframe or filepath to tabular data
            (e.g. csv, tsv, or Excel) detailing the process chains in the factory. 
            The chain in the first row of data is assumed to be the main 
            productChain.
        chain_list_sheet (str/None): Name of Excel sheet containing chains data
            Defaults to None.
        connections_file (DataFrame/str/None): Dataframe or filepath to tabular data 
            detailing the connections between the chains in the factory. 
            If None, uses chains_list_file.
            Defaults to None.
        connections_sheet (str/None): Name of Excel sheet containing connections
            data.
            Defaults to None.
        name (str, optional): The name of the factory. Defaults to False.

    Attributes:
        name (str): Factory name
        chains_df (data frame): Tabular data of the factory chains and the
            location of their data.
        connections_df (data frame): Tabuloar data of the connections
            between the factory chains. (optional)
        main_chain (str): the name of the factory's product chain, taken from
            the first row of chains_df.
        main_product (str): the name of the factory's main product, taken from 
            the first row of chains_df.
        chain_dict (dict): Dictionary of dictionaries containing process chain 
            objects in the factory. Each chain name is an entry key, with a 
            value of a dictionary containing the process chain object, name,
            product, and whether that product is a chain inflow or outflow.  
        **kwargs (dict): unused; allows for use of dictionaries with more variables
            than just used to define the class
    """

    # noinspection PyUnusedLocal
    def __init__(self, chain_list_file, chain_list_sheet=None, connections_file=None,
                 connections_sheet=None, name="Factory", outdir=False,
                 units_df=df_unit_library, units_df_basedir=dat.unit_process_library_file.parent,
                 **kwargs):

        logger.info(f"{name.upper()}: Initializing factory")
        self.name = name

        chain_list_df = iof.make_df(chain_list_file, chain_list_sheet, index=None)
        self.chain_dict = defaultdict(dict)

        # initalize individual chains
        for i, c in chain_list_df.iterrows():
            name = c[dat.chain_name]
            is_unit = False
            if i == 0:  # assumes first chain is main ProductChain 
                self.main_chain = name
                self.main_product = c[dat.chain_product]

            # creates chain DataFrame for those that are speficied as a single UnitProcess
            single_unit = iof.check_for_col(chain_list_df, dat.single_unit_chain, i)

            if type(single_unit) is str and single_unit not in dat.no_var:
                if single_unit in unit.df_unit_library.index.values:
                    unit_inflow = 'start'
                    unit_outflow = 'end'
                    if iof.clean_str(c[dat.chain_io][0]) == 'i':
                        unit_inflow = c[dat.chain_product]
                    elif iof.clean_str(c[dat.chain_io][0]) == 'o':
                        unit_outflow = c[dat.chain_product]
                    chain_data = [[unit_inflow, single_unit, unit_outflow]]
                    chain_header = [dat.inflow_col, dat.process_col, dat.outflow_col]
                    chain_file = pan.DataFrame(chain_data, columns=chain_header)
                    logger.debug(f"single unit process chain will be created for {single_unit}")
                    is_unit = True

            if is_unit is not True:  # uses user-specified chain linkage data
                if dat.chain_filepath not in chain_list_df or iof.clean_str(c[dat.chain_filepath]) in dat.same_xls:
                    chain_file = chain_list_file
                else:
                    chain_file = c[dat.chain_filepath]

            chain_sheet = iof.check_for_col(chain_list_df, dat.chain_sheetname,
                                            i)  # checks for Excel sheet of chain location
            logger.debug(f"{self.name.upper()}: building {name} chain using file: {chain_file}, sheet: {chain_sheet}")

            # intialize chain and store in chain dictionary with chain metadata
            self.chain_dict[name] = dict(chain=cha.ProductChain(chain_file,
                                         name=name,
                                         xls_sheet=chain_sheet,
                                         units_df=units_df,
                                         units_df_basedir=units_df_basedir),
                                         name=name,
                                         product=c[dat.chain_product],
                                         i_o=iof.clean_str(c[dat.chain_io][0]))

        # create DataFrame of connections betwen ProductChains, if extant
        if connections_file is None:  # assume same file as chain list
            if connections_sheet is None or connections_sheet in dat.no_var:
                self.connections_df = None
            self.connections_df = iof.make_df(chain_list_file, connections_sheet, index=None)
        elif connections_sheet is not None and connections_sheet not in dat.no_var:
            self.connections_df = iof.make_df(connections_file, connections_sheet, index=None)
        else:
            self.connections_df = None

        self.outdir = outdir if outdir else dat.path_outdir / f'{dat.timestamp_str}__factory_{self.name}'

        logger.info(f"{self.name.upper()}: Initalization successful")

    def balance(self, scenario=dat.default_scenario, product_qty=1.0, product=False, product_unit=False,
                product_io=False,
                upstream_outflows=False, upstream_inflows=False,
                downstream_outflows=False, downstream_inflows=False,
                aggregate_flows=False, net_flows=False, write_to_xls=True, outdir=False, subdir=False):
        """Calculates the mass balance of the factory using qty of main product

        Balances all UnitProcesses and Chains in the factory

        Based on a quantity of the factory's main product, calculates the 
        remaining quantities of all flows in the factory, assuming all unit 
        processes are well-specified with zero degrees of freedom.
        Processes the connections in the order that they are specified in the
        factory's connections DataFrame.

        Subfunctions used in Factory.balance() are at the end of this module.

        Args:
            product_qty (float): quantity of the product to balance on.
            product (str/bool):  product name. 
                If False, uses the default product in the chain object attributes.
                (Defaults to False)
            product_unit (str/bool): The unitProcess in the main ProductChain 
                where the factory product is located. 
                If False, assumes the product is a final outflow or inflow of 
                the main ProductChain
                (Defaults to False)
            product_io (str/bool): The flow type of the factory product. 
                If False, assumes the product is a final outflow or inflow of 
                the main ProductChain
                (Defaults to False)
            scenario (str): The var_df index ID of the scenario of variable
                values to use when balancing each UnitProcess.
                (Defaults to dat.default_scenario)
            write_to_xls (bool): If True, outputs the balance results to an Excel 
                workbook in dat.outdir.
                (Defaults to True)

        Returns:
            dictionary of factory inflow substances and total quantities
            dictionary of factory outflow substances and total quantities
        """

        logger.info(
            f"{self.name.upper()}: attempting to balance on {product_qty} of {self.chain_dict[self.main_chain]['product']}")

        # create flow dictionaries
        io_dicts = {
            'i': iof.nested_dicts(3, float),  # io_dicts['i'][chain][unit][substance] = float
            'o': iof.nested_dicts(3, float),  # io_dicts['o'][chain][unit][substance] = float
        }
        chain_intermediates_dict = iof.nested_dicts(3, float)
        intermediate_product_dict = defaultdict(
            float)  # tracks intra-factory flows (to be subtracted from factory totals)
        remaining_product_dict = iof.nested_dicts(4,
                                                  float)  # tracks products used for recycle flows (dict[i_o][chain][unit][substance] = float)
        internal_flows = []  # tracks intra-factory flows (origin/destination data)

        # balances main ProductChain
        main = self.chain_dict[self.main_chain]
        if product is False:
            product = main['product']

        (io_dicts['i'][main['name']],
         io_dicts['o'][main['name']],
         chain_intermediates_dict[main['name']],
         main_chain_internal_flows) = main['chain'].balance(product_qty,
                                                            product=product,
                                                            i_o=product_io,
                                                            unit_process=product_unit,
                                                            scenario=scenario)

        logger.debug(f"{self.name.upper()}: balanced main chain {main['name']} on {product_qty} of {product}")
        internal_flows.extend(main_chain_internal_flows)  # keeps track of flows betwen units

        # balances auxillary ProductChains
        if self.connections_df is not None:
            for dummy_index, row in self.connections_df.iterrows():

                # reset variables
                orig_product_io = iof.clean_str(row[dat.origin_io][0])
                orig_product = row[dat.origin_product]
                qty_remaining = 0

                dest_unit = False
                dest_unit_id = False
                dest_product = False
                dest_product_io = iof.clean_str(row[dat.dest_io][0])

                i_tmp = None
                o_tmp = None

                # identify origin (existing) and destination (connecting) ProductChains
                orig_chain = self.chain_dict[row[dat.origin_chain]]['chain']
                if not io_dicts[orig_product_io][orig_chain.name]:
                    raise KeyError(
                        f"{[orig_chain.name]} has not been balanced yet. Please check the order of your connections.")

                dest_chain = self.chain_dict[row[dat.dest_chain]]['chain']
                if dat.dest_unit in row:
                    if row[dat.dest_unit] in dest_chain.process_dict:
                        dest_unit = dest_chain.process_dict[row[dat.dest_unit]]
                        dest_unit_id = dest_unit.u_id

                # if destination chain connects to all UnitProcesses in origin chain, 
                # use totals flow values from origin chain, rather than individual UnitProcess data
                if row[dat.origin_unit] == dat.connect_all:
                    qty = io_dicts[orig_product_io][orig_chain.name]['chain totals'][orig_product]
                    orig_unit = False
                    logger.debug(f"using {qty} of {orig_product} from all units in {orig_chain.name}")

                else:
                    orig_unit = orig_chain.process_dict[row[dat.origin_unit]]

                    # processes substance name based on seperator and lookup key rules
                    orig_product = self.check_origin_product(orig_product, orig_unit, scenario)

                    # get product qty, checking to see if product has already been used elsewhere
                    qty = self.check_product_qty(orig_product, orig_product_io, orig_chain.name,
                                                 orig_unit.name, io_dicts, remaining_product_dict)

                if round(qty, dat.float_tol) < 0:
                    raise ValueError(f"{qty} of {orig_product}  from {orig_unit.name} in {orig_chain.name} < 0.")

                # For Recycle Connections
                if self.check_for_value(dat.replace, row) is True:
                    logger.debug(f"{self.name.upper()}: attempting to recycle {orig_product} from {orig_unit.name}")

                    new_chain_in_dict, new_chain_out_dict, qty_remaining, replace_flow = self.connect_recycle_flow(qty,
                                                                                                                   row,
                                                                                                                   scenario,
                                                                                                                   orig_chain,
                                                                                                                   orig_unit,
                                                                                                                   orig_product,
                                                                                                                   dest_chain,
                                                                                                                   dest_unit,
                                                                                                                   dest_product_io,
                                                                                                                   io_dicts,
                                                                                                                   chain_intermediates_dict)

                    io_dicts['i'][dest_chain.name] = new_chain_in_dict
                    io_dicts['o'][dest_chain.name] = new_chain_out_dict
                    remaining_product_dict[orig_product_io][orig_chain.name][orig_unit.name][
                        orig_product] = qty_remaining

                    logger.debug(
                        f"{self.name.upper()}: {remaining_product_dict[orig_product_io][orig_chain.name][orig_unit.name][orig_product]} {orig_product} remaining for {orig_chain.name}-{orig_unit.name}")

                # For Non-Recycle Connection
                else:
                    replace_flow = None

                    # allow for "connect as" products
                    dest_product = self.check_for_value(dat.dest_product, row, ifyes=row[dat.dest_product],
                                                        ifno=orig_product)

                    # balance auxillary chain based on qty of connecting product from already-calculated origin chain
                    logger.debug(
                        f"sending {qty} of {orig_product} to {dest_chain.name} as {dest_product} ({dest_product_io}-flow)")

                    (i_tmp, o_tmp,
                     chain_intermediates_dict[dest_chain.name],
                     chain_internal_flows) = dest_chain.balance(qty=qty,
                                                                product=dest_product,
                                                                product_alt_name=orig_product,
                                                                i_o=dest_product_io,
                                                                unit_process=dest_unit_id,
                                                                scenario=scenario, )

                    internal_flows.extend(chain_internal_flows)

                    # add chain inflow/outflow data to factory inflow/outflow dictionaries
                    # if chain already exists, add flow values instead of replacing
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

                    logger.debug(
                        f"{qty} of {orig_product} as product from {orig_chain.name} ({orig_product_io}) sent to to {dest_chain.name} ({dest_product_io})")

                # FOR ALL CONNECTIONS
                # add intra-chain product qty to intra-factory flow dictionary (to be deleted from factory total in/out)
                intermediate_product_dict[orig_product] += (qty - qty_remaining)
                logger.debug(f"{qty - qty_remaining} of {orig_product} added to intermediate_product_dict")

                # update list of intra-factory flows for documentation output
                internal_flows.append(
                    self.describe_internal_flow(row, qty, qty_remaining, orig_chain, orig_unit, orig_product,
                                                orig_product_io, dest_chain, dest_unit, dest_product, dest_product_io,
                                                replace_flow))

        # Calculate Factory-level inflows and outflows
        factory_totals = {
            'i': defaultdict(float),
            'o': defaultdict(float)
        }

        # aggregate chain totals 
        for chain in io_dicts['i']:
            for inflow, qty in io_dicts['i'][chain]['chain totals'].items():
                factory_totals['i'][inflow] += qty
        for chain in io_dicts['o']:
            for outflow, qty in io_dicts['o'][chain]['chain totals'].items():
                factory_totals['o'][outflow] += qty

        # remove inter-chain flows
        for io_dict in factory_totals:
            for product, qty in intermediate_product_dict.items():
                factory_totals[io_dict][product] -= qty  # removes intermediate product quantities

        # add additional upstream/downstream flows for factory inflows and outflows, based on factory totals
        if type(upstream_outflows) is list or type(
                upstream_inflows) is list:  # add upstream emissions to factory output
            factory_totals = self.add_updownstream_flows(factory_totals,
                                                         io='i',
                                                         inflow_list=upstream_inflows,
                                                         df_inflows=df_upstream_inflows,
                                                         outflow_list=upstream_outflows,
                                                         df_outflows=df_upstream_outflows)

        if type(downstream_outflows) is list or type(
                downstream_inflows) is list:  # add downstream emissions to factory output
            factory_totals = self.add_updownstream_flows(factory_totals,
                                                         io='o',
                                                         inflow_list=downstream_inflows,
                                                         df_inflows=df_downstream_inflows,
                                                         outflow_list=downstream_outflows,
                                                         df_outflows=df_downstream_outflows)

        # aggregate flows that have a specified prefix 
        aggregated_df = self.aggregate_flows(aggregate_flows, inflow_dict=factory_totals['i'],
                                             outflow_dict=factory_totals['o'])

        # calculate net flows
        net_df = self.net_flows(net_flows, factory_totals, aggregated_df)

        # output to file
        if write_to_xls is True:
            self.factory_to_excel(io_dicts, factory_totals, internal_flows,
                                  scenario, product_qty, aggregated_df, net_df, outdir, subdir)

        logger.debug(f"successfully balanced factory on {product_qty} of {self.chain_dict[self.main_chain]['product']}")

        return factory_totals['i'], factory_totals['o'], aggregated_df, net_df

    def diagram(self, view=False, save=True, outdir=False):
        """ Outputs a diagram of factory flows to file using Graphviz

        Using Graphviz, takes the unit process names, sets of inflows and 
        outflows, and the specified linkages of the factory to generate a
        diagram of the chain as a png and svg.

        Diagram subfunctions are at the end of this module.

        NB: requires many subcases to achieve correct flow grouping and arrow
            directionality
        
        Args:
            view(bool): If True, displays the diagram in the system
                viewer. 
                (Defaults to True)
        """

        outdir = outdir if outdir else self.outdir
        filename = f'{self.name}_f_{dat.timestamp_str}'

        factory_diagram = Digraph(name="factory")
        factory_diagram.attr('node', shape='box', color='black')

        factory_subgraphs = dict()  # for ProductChains

        # Subgraph for Factory inflows and outflows (not intra-factory flows)
        io_diagram = Digraph(name=filename, directory=outdir, format='png', )
        io_diagram.attr('node', shape='box', color='white')

        # for each productChain, generate GraphViz object
        for c in self.chain_dict:
            d_kwargs = dict(view=False,
                            outdir=f'{outdir}/{self.name}')

            diagram_dict = dict(diagram=self.chain_dict[c]['chain'].diagram(**d_kwargs),
                                process_list=self.chain_dict[c]['chain'].process_list,
                                name=self.chain_dict[c]['name'], connect=[])

            # identify main chain
            if diagram_dict['name'] == self.main_chain:
                diagram_dict['diagram'].attr(rank='min')

            factory_subgraphs[self.chain_dict[c]['name']] = diagram_dict

        # connect chain subgraphs using inter-chain flows
        if self.connections_df is not None:
            factory_diagram = self.connect_subgraphs(factory_diagram, factory_subgraphs)

        # add Factory-level inflows and outflows
        for d in factory_subgraphs:
            chain = factory_subgraphs[d]['name']
            diagram = factory_subgraphs[d]['diagram']
            process_list = factory_subgraphs[d]['process_list']

            # for each UnitProcess in each ProductChain subgraph
            for i, unit in enumerate(process_list):
                process = unit['process'].name
                inflows = '\n'.join(unit['process'].inflows)
                outflows = '\n'.join(unit['process'].outflows)

                if self.connections_df is not None:
                    for dummy_index, c in self.connections_df.iterrows():

                        origin_product = c[dat.origin_product]
                        product = self.check_for_value(col=dat.dest_product, row=c, ifyes=c[dat.dest_product],
                                                       ifno=c[dat.origin_product])

                        # get inflows and outflows of each unit, using the correct product name
                        if chain == c[dat.origin_chain]:
                            if process == c[dat.origin_unit] or c[dat.origin_unit] == dat.connect_all:
                                if iof.clean_str(c[dat.origin_io][0]) == 'i':
                                    inflows = self.clean_str_in_list(origin_product, inflows)
                                if iof.clean_str(c[dat.origin_io][0]) == 'o':
                                    outflows = self.clean_str_in_list(origin_product, outflows)

                        if chain == c[dat.dest_chain]:
                            if iof.clean_str(c[dat.dest_io][0]) == 'i' and unit == process_list[0]:
                                inflows = self.clean_str_in_list(product, inflows)
                            if iof.clean_str(c[dat.dest_io][0]) == 'o' and unit == process_list[-1]:
                                outflows = self.clean_str_in_list(product, outflows)

                if i == 0:  # if first UnitProcess in ProductChain
                    io_diagram, factory_diagram = self.add_flows_to_graph(inflows, 'i', chain, process, io_diagram,
                                                                          factory_diagram)

                    if len(process_list) == 1:
                        io_diagram, factory_diagram = self.add_flows_to_graph(outflows, 'o', chain, process, io_diagram,
                                                                              factory_diagram)

                    elif outflows != unit['o']:
                        outflows = self.clean_str_in_list(unit['o'], outflows)
                        io_diagram, factory_diagram = self.add_flows_to_graph(outflows, 'o', chain, process, io_diagram,
                                                                              factory_diagram)

                # if intermediate UnitProcess in ProductChain
                elif i < len(process_list) - 1:
                    if inflows != unit['i']:
                        inflows = self.clean_str_in_list(unit['i'], inflows)
                        io_diagram, factory_diagram = self.add_flows_to_graph(inflows, 'i', chain, process, io_diagram,
                                                                              factory_diagram)

                    if outflows != unit['o']:
                        outflows = self.clean_str_in_list(unit['o'], outflows)
                        io_diagram, factory_diagram = self.add_flows_to_graph(outflows, 'o', chain, process, io_diagram,
                                                                              factory_diagram)

                else:  # if last UnitProcess in ProductChain
                    if inflows != unit['i']:
                        inflows = self.clean_str_in_list(unit['i'], inflows)
                        io_diagram, factory_diagram = self.add_flows_to_graph(inflows, 'i', chain, process, io_diagram,
                                                                              factory_diagram)

                    io_diagram, factory_diagram = self.add_flows_to_graph(outflows, 'o', chain, process, io_diagram,
                                                                          factory_diagram)

        for diagram in factory_subgraphs:
            factory_subgraphs[diagram]['diagram'].attr('graph', name='cluster')
            factory_diagram.subgraph(factory_subgraphs[diagram]['diagram'])

        io_diagram.subgraph(factory_diagram)

        io_diagram.engine = 'circo'

        if view is True:
            io_diagram.view()

        if save is True:
            io_diagram.render()  # save as png
            io_diagram.format = 'svg'
            io_diagram.render()  # save as svg

        logger.debug(f"created diagram for {self.name} factory")

    def run_scenarios(self, scenario_list,
                      product_qty=1.0, product=False, product_unit=False, product_io=False,
                      upstream_outflows=False, upstream_inflows=False, downstream_outflows=False,
                      downstream_inflows=False, aggregate_flows=False, net_flows=False, write_to_xls=True,
                      factory_xls=True, outdir=False, file_id='', subdir='scenario factories'):
        """Balances the Factory using different sets of variable values.
        Creates a spreadsheet comparing inflows and outflows for the factory for each scenario.

        Args:
            all arguments from Factory.balance() except scenario and write_to_xls 
            scenario_list (list[str]): List of scenario variable values to use, 
                each corresponding to a matching row index in each unit 
                process's var_df. 
            file_id (str): Additional text to add to filename.
                (Defaults to an empty string)

            factory_xls: 

        Returns:
            Dataframe of compared inflows
            Dataframe of compared outflows

        """
        if outdir is False:
            outdir = self.outdir

        scenario_dict = iof.nested_dicts(3)

        for scenario in scenario_list:
            f_in, f_out, agg_df, net_df = self.balance(product_qty=product_qty,
                                                       product=product,
                                                       product_unit=product_unit,
                                                       product_io=product_io,
                                                       scenario=scenario,
                                                       upstream_outflows=upstream_outflows,
                                                       upstream_inflows=upstream_inflows,
                                                       downstream_outflows=downstream_outflows,
                                                       downstream_inflows=downstream_inflows,
                                                       aggregate_flows=aggregate_flows,
                                                       net_flows=net_flows,
                                                       write_to_xls=factory_xls,
                                                       outdir=outdir,
                                                       subdir=subdir)

            scenario_dict['i'][scenario] = f_in
            scenario_dict['o'][scenario] = f_out

            if type(aggregate_flows) is list:
                if 'inflows' in agg_df:
                    scenario_dict['agg_i'][scenario] = agg_df['inflows'].rename(scenario)
                else:
                    scenario_dict['agg_i'][scenario] = pan.DataFrame()
                if 'outflows' in agg_df:
                    scenario_dict['agg_o'][scenario] = agg_df['outflows'].rename(scenario)
                else:
                    scenario_dict['agg_o'][scenario] = pan.DataFrame()

            if type(net_flows) is list:
                scenario_dict['net'][scenario] = net_df['difference'].rename(scenario)

        inflows_df = iof.mass_energy_df(scenario_dict['i'])
        outflows_df = iof.mass_energy_df(scenario_dict['o'])

        if type(aggregate_flows) is list:
            first = True
            for scenario in scenario_list:
                if first is True:
                    aggregated_inflows_df = scenario_dict['agg_i'][scenario].copy()
                    aggregated_outflows_df = scenario_dict['agg_o'][scenario].copy()

                    first = False
                else:
                    aggregated_inflows_df = pan.concat([aggregated_inflows_df, scenario_dict['agg_i'][scenario]],
                                                       ignore_index=False, sort=False, axis=1)
                    aggregated_outflows_df = pan.concat([aggregated_outflows_df, scenario_dict['agg_o'][scenario]],
                                                        ignore_index=False, sort=False, axis=1)
        else:
            aggregated_inflows_df = pan.DataFrame()
            aggregated_outflows_df = pan.DataFrame()

        if type(net_flows) is list:
            first = True
            for scenario in scenario_list:
                if first is True:
                    net_df = scenario_dict['net'][scenario].copy()
                    first = False
                else:
                    net_df = pan.concat([net_df, scenario_dict['net'][scenario]], ignore_index=False, sort=False,
                                        axis=1)
        else:
            net_df = pan.DataFrame()

        if write_to_xls is True:
            if product is False:
                product = self.main_product

            meta_df = iof.metadata_df(user=dat.user_data,
                                      name=self.name,
                                      level="Factory",
                                      scenario=" ,".join(scenario_list),
                                      product=product,
                                      product_qty=product_qty)

            df_list = [meta_df, inflows_df, outflows_df]
            sheet_list = ["meta", "inflows", "outflows"]

            if type(aggregate_flows) is list:
                df_list.extend([aggregated_inflows_df, aggregated_outflows_df])
                sheet_list.extend(["aggr inflows", "aggr outflows"])

            if type(net_flows) is list:
                df_list.append(net_df)
                sheet_list.append('net flows')

            iof.write_to_xls(df_or_df_list=df_list,
                             sheet_list=sheet_list,
                             filedir=outdir,
                             filename=f'{self.name}_f_multi_{dat.timestamp_str}')

        return inflows_df, outflows_df, aggregated_inflows_df, aggregated_outflows_df, net_df

    def run_sensitivity(self, product_qty, scenario, chain_name, unit_name, variable, variable_options=[],
                        fixed_vars=False,
                        product=False, product_unit=False, product_io=False, upstream_outflows=False,
                        upstream_inflows=False,
                        downstream_outflows=False, downstream_inflows=False, aggregate_flows=False, net_flows=False,
                        write_to_xls=True, individual_xls=False, outdir=False, id=''):
        """Balances the factory on the same quantity for a list of different scenarios.
        Outputs a file with total inflows and outflows for the factory for each scenario.

        Args:
            all arguments from Factory.balance() 
            chain_name (str or list; must be same type as unit_name)
            unit_name (str or list; must be same type as chain_name)
            variable
            variable_options
            fixed_vars
            id (str): optional file name prefix


        Returns:
            Dataframe of compared inflows
            Dataframe of compared outflows

        """

        outdir = outdir if outdir else self.outdir / f'{id}sensitivity/' / f'{variable}'

        scenario_dict = iof.nested_dicts(3)

        units = []
        original_var_dfs = []

        if type(unit_name) is list:
            for i, unit in enumerate(unit_name):
                units.append(self.chain_dict[chain_name[i]]['chain'].process_dict[unit])

        else:
            units = [self.chain_dict[chain_name]['chain'].process_dict[unit_name]]

        # change variables which will remain static between sensitivity runs
        for unit in units:
            original_var_dfs.append(unit.var_df.copy())

        if type(fixed_vars) is list:
            for fixedvar, fixedvalue in fixed_vars:
                for unit in units:
                    if scenario in unit.var_df.index: 
                        unit.var_df.loc[scenario, fixedvar.lower()] = fixedvalue
                        logger.debug(f"{variable} for {unit} ({scenario} set to {fixedvalue}) (fixed over all sensitivity analyses)")
                    else:
                        unit.var_df.loc[dat.default_scenario, fixedvar.lower()] = fixedvalue
                        logger.debug(f"{variable} for {unit} ({dat.default_scenario} set to {fixedvalue}) (fixed over all sensitivity analyses)")

        # evaluate over varying variables
        for value in variable_options:
            for unit in units:
                if scenario in unit.var_df.index: 
                    unit.var_df.loc[scenario, variable.lower()] = value
                    logger.debug(f"{variable} for {unit.name} ({scenario}) set to {value})")
                else:
                    unit.var_df.loc[dat.default_scenario, variable.lower()] = value
                    logger.debug(f"{variable} for {unit.name} ({dat.default_scenario}) set to {value})")

            f_in, f_out, agg_df, net_df = self.balance(product_qty=product_qty,
                                                       product=product,
                                                       product_unit=product_unit,
                                                       product_io=product_io,
                                                       scenario=scenario,
                                                       upstream_outflows=upstream_outflows,
                                                       upstream_inflows=upstream_inflows,
                                                       downstream_outflows=downstream_outflows,
                                                       downstream_inflows=downstream_inflows,
                                                       aggregate_flows=aggregate_flows,
                                                       net_flows=net_flows,
                                                       write_to_xls=individual_xls,
                                                       outdir=f"{outdir}/{value}")

            scenario_dict['i'][f'{scenario}_{unit_name}-{variable}_{value}'] = f_in
            scenario_dict['o'][f'{scenario}_{unit_name}-{variable}_{value}'] = f_out

            try:
                scenario_dict['agg_i'][f'{scenario}_{unit_name}-{variable}_{value}'] = agg_df['inflows'].rename(
                    f'{scenario}_{unit_name}-{variable}_{value}')
                has_agg_in = True
            except:
                logger.debug("No agg inflows defined")
                has_agg_in = False

            try:
                scenario_dict['agg_o'][f'{scenario}_{unit_name}-{variable}_{value}'] = agg_df['outflows'].rename(
                    f'{scenario}_{unit_name}-{variable}_{value}')
                has_agg_out = True
            except:
                logger.debug("No agg outflows defined")
                has_agg_out = False

            try:
                scenario_dict['net'][f'{scenario}_{unit_name}-{variable}_{value}'] = net_df['difference'].rename(
                    f'{scenario}_{unit_name}-{variable}_{value}')
                has_net = True
            except:
                logger.debug("No net flows defined")
                has_net = False

        inflows_df = iof.mass_energy_df(scenario_dict['i'])
        outflows_df = iof.mass_energy_df(scenario_dict['o'])

        if product is False:
            product = self.main_product

        meta_df = iof.metadata_df(user=dat.user_data,
                                  name=self.name,
                                  level="Factory",
                                  scenario=f'{scenario}-{unit_name}-{variable}-sensitivity',
                                  product=product,
                                  product_qty=product_qty)

        dfs = [meta_df, inflows_df, outflows_df, ]
        sheets = ["meta", "inflows", "outflows"]

        # generate dfs for agg inflows, agg outflows, and net flows, if extant
        agg_flow_dfs = [None, None, None]

        for i, bool, name in [(0, has_agg_in, "agg_i"), (1, has_agg_out, "agg_o"), (2, has_net, "net")]:
            df = None
            if bool is True:
                first = True
                for scenario in scenario_dict[name].keys():
                    if first is True:
                        df = scenario_dict[name][scenario].copy()
                        first = False
                    else:
                        df = pan.concat([df, scenario_dict[name][scenario]], ignore_index=False, sort=False, axis=1)

                dfs.append(df)
                sheets.append(name)
                agg_flow_dfs[i] = df

        iof.write_to_xls(df_or_df_list=dfs,
                         sheet_list=sheets,
                         filedir=outdir,
                         filename=f'{self.name}_{id}f_sens_{dat.timestamp_str}')

        for i, unit in enumerate(units):
            unit.var_df = original_var_dfs[i].copy()

        return inflows_df, outflows_df, agg_flow_dfs[0], agg_flow_dfs[1], agg_flow_dfs[2]  # aggregated_dict

    ###############################################################################
    # SUBFUNCTIONS
    ###############################################################################

    # BALANCE SUBFUNCTIONS
    def check_origin_product(self, origin_product, orig_unit, scenario):
        """parses separators and lookup variables in product name
            Used in self.balance() (above)
        """

        if dat.ignore_sep in origin_product:
            if origin_product.split(dat.ignore_sep)[0] in lookup_var_dict:
                if scenario in orig_unit.var_df.index:
                    lookup_substance = orig_unit.var_df.at[
                        scenario, lookup_var_dict[origin_product.split(dat.ignore_sep)[0]]['lookup_var']]
                else:
                    lookup_substance = orig_unit.var_df.at[
                        dat.default_scenario, lookup_var_dict[origin_product.split(dat.ignore_sep)[0]]['lookup_var']]
                origin_product = lookup_substance + dat.ignore_sep + origin_product.split(dat.ignore_sep)[1]
        elif origin_product in lookup_var_dict:
            if scenario in orig_unit.var_df.index:
                origin_product = orig_unit.var_df.at[scenario, lookup_var_dict[origin_product]['lookup_var']]
            else:
                origin_product = orig_unit.var_df.at[
                    dat.default_scenario, lookup_var_dict[origin_product]['lookup_var']]
        return origin_product

    def check_product_qty(self, product, product_io, chain_name, unit_name, io_dicts, remaining_product_dict):
        """checks if product qty needs to account for use in previous recycled flows
            Used in self.balance() (above)
        """

        if product in remaining_product_dict[product_io][chain_name][unit_name]:
            qty = remaining_product_dict[product_io][chain_name][unit_name][product]
            logger.debug(f"{product} found in remaining_product_dict, {qty} unused.")
        else:
            qty = io_dicts[product_io][chain_name][unit_name][product]
            logger.debug(f"using {qty} of {product} from {unit_name} in {chain_name}")

        return qty

    def check_for_value(self, col, row, ifyes=True, ifno=False):
        """check whether a value exists in a DataFrame, and return a specified
            value in either case. (Defaults to True/False)
            Used in self.balance() and self.diagram() (above)
        """

        if col in row and type(row[col]) is str and row[col] not in dat.no_var:
            return ifyes
        else:
            return ifno

    def check_for_recycle_fractions(self, qty, row):
        """check whether a recycle flow has a purge fraction or maximum replace fraction.
            Used in self.connect_recycle_flow() (below)
        """

        purge = 0
        max_replace_fraction = 1.0

        if dat.purge_fraction in row:
            if row[dat.purge_fraction] not in dat.no_var:
                if type(row[dat.purge_fraction]) in [float, int] and not isnan(row[dat.purge_fraction]):
                    calc.check_qty(row[dat.purge_fraction], fraction=True)
                    purge = qty * row[dat.purge_fraction]
                    qty = qty - purge
                    logger.debug(f"purge: {purge}, new qty: {qty}")

        if dat.max_replace_fraction in row:
            if row[dat.max_replace_fraction] not in dat.no_var:
                if type(row[dat.max_replace_fraction]) in [float, int] and not isnan(row[dat.max_replace_fraction]):
                    calc.check_qty(row[dat.max_replace_fraction], fraction=True)
                    max_replace_fraction = row[dat.max_replace_fraction]

        if qty < 0:
            raise ValueError(f"{qty} < 0 after calculating purge ({purge})")

        return qty, max_replace_fraction

    def check_for_lookup(self, col, df, unit, scenario, check_if_in_list=False):
        """check whether a dataframe value is a lookup value and/or in a list
            Used in self.connect_recycle_flow() (below)
        """

        in_list = None

        if df[col] in lookup_var_dict:
            if scenario in unit.var_df.index:
                flow = unit.var_df.at[scenario, lookup_var_dict[df[col]]['lookup_var']]
            else:
                flow = unit.var_df.at[dat.default_scenario, lookup_var_dict[df[col]]['lookup_var']]
            if type(check_if_in_list) is list:
                if df[col] in check_if_in_list:
                    in_list = True
                else:
                    in_list = False

        else:
            flow = df[col]

        return flow, in_list

    def connect_recycle_flow(self, qty, row, scenario, orig_chain, orig_unit, orig_product, dest_chain, dest_unit,
                             dest_product_io, io_dicts, chain_intermediates_dict):
        """recalculates chain flow data for a recycled flow connection
            used in self.balance() (above)
        """

        qty, max_replace_fraction = self.check_for_recycle_fractions(qty, row)

        # check if flow to be replaced is a lookup variable and/or a fuel
        replace_flow, replace_fuel = self.check_for_lookup(col=dat.replace,
                                                           df=row,
                                                           unit=dest_unit,
                                                           scenario=scenario,
                                                           check_if_in_list=dat.fuel_flows)

        if replace_flow not in io_dicts[dest_product_io][dest_chain.name][dest_unit.name]:
            raise ValueError(
                f"{replace_flow} not found in {dest_chain.name}'s {dest_unit.name} {dest_product_io}-flows")

        # kwargs for UnitProcess recycle function
        r_kwargs = dict(original_inflows_dict=io_dicts['i'][dest_chain.name][dest_unit.name],
                        original_outflows_dict=io_dicts['o'][dest_chain.name][dest_unit.name],
                        recycled_qty=qty,
                        recycle_io=dest_product_io,
                        recyclate_flow=orig_product,
                        toBeReplaced_flow=replace_flow,
                        max_replace_fraction=max_replace_fraction,
                        scenario=scenario)

        # check if energy is recycled to replace combusted fuel
        if replace_fuel is True:
            for string in dat.energy_flows:
                if orig_product.startswith(string) or orig_product.endswith(string):
                    logger.debug("replacing fuel with energy")

                    # recalculate fuel and emissions qtys
                    i_tmp, o_tmp, qty_remaining = dest_unit.recycle_energy_replacing_fuel(**r_kwargs)
                    break

        else:  # in all non energy-to-fuel cases, assume one-to-one replacement
            i_tmp, o_tmp, qty_remaining = dest_unit.recycle_1to1(**r_kwargs)

        logger.debug(
            f"{self.name.upper()}: recycled {qty} of {orig_product}  from {orig_unit.name} in {orig_chain.name}"
            f"to replace {replace_flow} in {dest_unit.name} in {dest_chain.name}")

        new_chain_in_dict, new_chain_out_dict = self.update_chain_dict_after_recycle(
            chain_in_dict=io_dicts['i'][dest_chain.name],
            chain_out_dict=io_dicts['o'][dest_chain.name],
            chain_name=dest_chain.name,
            unit_name=dest_unit.name,
            new_in=i_tmp,
            new_out=o_tmp,
            chain_intermediates_dict=chain_intermediates_dict)

        return new_chain_in_dict, new_chain_out_dict, qty_remaining, replace_flow

    def update_chain_dict_after_recycle(self, chain_in_dict, chain_out_dict, chain_name, unit_name, new_in, new_out,
                                        chain_intermediates_dict):
        """updates chain dictionaries using recalculated flow data
            used in self.balance() (above)
        """

        chain_in_dict[unit_name].clear()
        chain_out_dict[unit_name].clear()

        chain_in_dict[unit_name] = new_in
        chain_out_dict[unit_name] = new_out

        logger.debug("replaced IO Dicts:")
        logger.debug(chain_in_dict[unit_name])
        logger.debug(chain_out_dict[unit_name])

        # recalculate chain totals using rebalanced unit
        new_chain_totals = {
            'i': defaultdict(float),
            'o': defaultdict(float)
        }

        # resum total flows
        for process, inflows_dict in chain_in_dict.items():
            if process != 'chain totals':
                for inflow, i_qty in inflows_dict.items():
                    new_chain_totals['i'][inflow] += i_qty
        for process, outflows_dict in chain_out_dict.items():
            if process != 'chain totals':
                for outflow, o_qty in outflows_dict.items():
                    new_chain_totals['o'][outflow] += o_qty

        # re-remove intermediate products
        for io in new_chain_totals:
            for intermediate_product, int_qty in chain_intermediates_dict[chain_name].items():
                new_chain_totals[io][intermediate_product] -= int_qty

        chain_in_dict["chain totals"].clear()
        chain_out_dict["chain totals"].clear()

        chain_in_dict["chain totals"] = new_chain_totals['i']
        chain_out_dict["chain totals"] = new_chain_totals['o']

        return chain_in_dict, chain_out_dict

    def describe_internal_flow(self, row, qty, qty_remaining, orig_chain, orig_unit, orig_product, orig_product_io,
                               dest_chain, dest_unit, dest_product, dest_product_io, replace_flow):
        """formats data about an intra-factory flow for output to dataframe
            used in self.balance() (above)
        """

        # copy to avoid overwriting
        orig_chain_name = orig_chain.name
        dest_chain_name = dest_chain.name

        if orig_unit and orig_unit.name:
            orig_unit_name = orig_unit.name
        elif row[dat.origin_unit] == dat.connect_all:
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

        if replace_flow is not None:
            return [orig_chain_name, orig_unit_name, f'{orig_product} REPLACING {replace_flow}', (qty - qty_remaining),
                    dest_chain_name, dest_unit_name]
        else:
            return [orig_chain_name, orig_unit_name, f'{orig_product} AS {dest_product}', (qty - qty_remaining),
                    dest_chain_name, dest_unit_name]

    def add_updownstream_flows(self, factory_totals, io, inflow_list=None, df_inflows=None, outflow_list=None,
                               df_outflows=None):
        """adds additional flows to factory total inflows and outflows based on qty of factory total inflows or outflows. 
            e.g. for life cycle assessment background systems
            used in self.balance() (above)

            args:
                io (str): when "i", computes additional flows based on factory inflows, 
                    when "o", based on outflows
                inflow_list: list of additional inflows to compute
                df_inflows: dataframe with factory flow names as index and columns with additional inflow data
                outflow_list: list of additional outflows to compute
                df_outflows: dataframe with factory flow names as index and columns with additional outflow data

        """
        if io not in ['i', 'o']:
            raise ValueError("io must be i (for inflows) or o (for outflows)")
        if io == 'i':
            loc = 'up'
        else:
            loc = 'down'

        # initalize dicts for up/downstream flows to be added to factory totals
        additional_inflows = defaultdict(float)
        additional_outflows = defaultdict(float)

        # initalize dicts for balancer terms to close mass balance (added to opposite flow dict of )
        balancers_in = defaultdict(float)
        balancers_out = defaultdict(float)

        # for each relevant factory flow (inflows for upstream, outflows for downstream)
        for f in factory_totals[io]:
            factory_flow = f
            factory_flow_qty = factory_totals[io][f]
            if dat.ignore_sep in factory_flow:
                factory_flow = factory_flow.split(dat.ignore_sep)[0]

            # check for and calculate updownstream outflows 
            if type(outflow_list) is list:
                for e in outflow_list:
                    emission = iof.clean_str(e)
                    total_e_qty = 0
                    logger.debug(f"checking for upstream {emission} for {factory_flow}")
                    if factory_flow in df_outflows.index:  # if factory flow not found, then skip
                        logger.debug(f"{factory_flow} found")
                        emission_flow = f'{e}{dat.ignore_sep}{loc}stream ({factory_flow})'
                        emission_qty = factory_flow_qty * df_outflows.at[factory_flow, emission]
                        logger.debug(
                            f"{round(emission_qty, 4)} of {emission} calculated for {round(factory_flow_qty, 4)} of {factory_flow} using factor of {round(df_outflows.at[factory_flow, emission], 4)}")
                        total_e_qty += emission_qty

                        if round(emission_qty, dat.float_tol) < 0:
                            raise ValueError(f'emission_qty ({emission_qty}) should not be negative')
                        else:
                            additional_outflows[emission_flow] += emission_qty

                    balancers_in[f"BALANCER for {e} updownstream"] += total_e_qty

            # check for and calculate updownstream inflows
            if type(inflow_list) is list:
                for e in inflow_list:
                    emission = iof.clean_str(e)
                    total_e_qty = 0
                    logger.debug(f"checking for upstream {emission} for {factory_flow}")
                    if factory_flow in df_inflows.index:  # if factory flow not found, then skip
                        logger.debug(f"{factory_flow} found")
                        emission_flow = f'{e}{dat.ignore_sep}{loc}stream ({factory_flow})'
                        emission_qty = factory_flow_qty * df_inflows.at[factory_flow, emission]
                        logger.debug(
                            f"{round(emission_qty, 4)} of {emission} calculated for {round(factory_flow_qty, 4)} of {factory_flow} using factor of {round(df_inflows.at[factory_flow, emission], 4)}")
                        total_e_qty += emission_qty

                        if round(emission_qty, dat.float_tol) < 0:
                            raise ValueError(f'emission_qty ({emission_qty}) should not be negative')
                        else:
                            additional_inflows[emission_flow] += emission_qty

                    balancers_out[f"BALANCER for {e} updownstream"] += total_e_qty

        for flow in additional_inflows:
            factory_totals["i"][flow] = additional_inflows[flow]
        for flow in additional_outflows:
            factory_totals["o"][flow] = additional_outflows[flow]

        for e in balancers_in:
            factory_totals["i"][e] = balancers_in[e]
        for e in balancers_out:
            factory_totals["o"][e] = balancers_out[e]

        return factory_totals

    def factory_to_excel(self, io_dicts, factory_totals, internal_flows, scenario, product_qty, aggregated_df, net_df,
                         outdir=False, subdir=False):
        """formats factory data to datafames and outputs to excel file
            used in self.balance() (above)
        """

        outdir = outdir if outdir else self.outdir
        filename = f'{self.name}_f_{scenario}_{dat.timestamp_str}'

        meta_df = iof.metadata_df(user=dat.user_data, name=self.name,
                                  level="Factory", scenario=scenario, product=self.main_product,
                                  product_qty=product_qty)

        # make totals dataframe with segregated mass and energy flows
        totals_dict = iof.nested_dicts(2)
        totals_dict['factory inflows'] = factory_totals['i']
        totals_dict['factory outflows'] = factory_totals['o']
        totals_df = iof.make_df(totals_dict, drop_zero=True)
        totals_df = iof.mass_energy_df(totals_df, aggregate_consumed=True)

        # make dataframe for intra-factory flows                
        internal_flows_header = ['origin chain', 'origin unit', 'flow product', 'quantity', 'destination chain',
                                 'destination unit']
        internal_flows_df = pan.DataFrame(internal_flows, columns=internal_flows_header)

        # shorten factory names to prevent issue with Excel filename length limits
        if len(self.name) > 17:
            factory_name = self.name[:17] + '...'
        else:
            factory_name = self.name

        # begin list of dataframes to write to Excel file
        df_list = [meta_df, totals_df]
        sheet_list = ['metadata', f'{factory_name} totals']

        if type(aggregated_df) is pan.DataFrame:
            df_list.append(aggregated_df)
            sheet_list.append('aggregated flows')

        if type(net_df) is pan.DataFrame:
            df_list.append(net_df)
            sheet_list.append('net flows')

        df_list.append(internal_flows_df)
        sheet_list.append('internal flows')

        # intalizes matricies for all flows per unit processes
        all_inflows = defaultdict(lambda: defaultdict(float))
        all_outflows = defaultdict(lambda: defaultdict(float))

        # create chain inflows/outflows spreadsheets
        chain_inflows_dict = iof.nested_dicts(2)
        chain_outflows_dict = iof.nested_dicts(2)

        for chain in io_dicts['i']:
            chain_inflows_dict[chain] = io_dicts['i'][chain]['chain totals']
            chain_outflows_dict[chain] = io_dicts['o'][chain]['chain totals']

            for process_dict in io_dicts['i'][chain]:
                if 'total' not in process_dict:
                    for substance, qty in io_dicts['i'][chain][process_dict].items():
                        all_inflows[process_dict][substance] = qty
                    for substance, qty in io_dicts['o'][chain][process_dict].items():
                        all_outflows[process_dict][substance] = qty

        # generate and append new dataframes to file
        all_inflows_df = iof.make_df(all_inflows, drop_zero=True)
        all_inflows_df = iof.mass_energy_df(all_inflows_df, totals=False)
        df_list.append(all_inflows_df)
        sheet_list.append("unit inflow matrix")

        all_outflows_df = iof.make_df(all_outflows, drop_zero=False)
        all_outflows_df = iof.mass_energy_df(all_outflows_df, totals=False)
        df_list.append(all_outflows_df)
        sheet_list.append("unit outflow matrix")

        chain_inflows_df = iof.mass_energy_df(chain_inflows_dict)
        chain_outflows_df = iof.mass_energy_df(chain_outflows_dict)
        df_list.extend([chain_inflows_df, chain_outflows_df])
        sheet_list.extend(["chain totals in", "chain totals out"])

        # output to all Dataframes to single Excel file
        iof.write_to_xls(df_list, sheet_list=sheet_list,
                         filedir=outdir, filename=filename, subdir=subdir)

    def aggregate_flows(self, aggregate_flows, inflow_dict, outflow_dict):
        """Creates dataframe of specified aggregated flows
        """
        if not aggregate_flows or type(aggregate_flows) is not list:
            return pan.DataFrame()

        aggregated_dict = iof.nested_dicts(2)

        for flow in aggregate_flows:
            for inflow in inflow_dict:
                if inflow.lower().startswith(flow.lower()):
                    aggregated_dict['inflows'][flow] += inflow_dict[inflow]

            for outflow in outflow_dict:
                if outflow.lower().startswith(flow.lower()):
                    aggregated_dict['outflows'][flow] += outflow_dict[outflow]

        # make aggregate flows dataframe
        return iof.make_df(aggregated_dict, drop_zero=True)

    def net_flows(self, net_tuples, io_dicts, aggregated_df=None):
        """ Calculates net flows given specified minuend and subtrahend

        minuend - subtrahend = difference
        """
        if not net_tuples or type(net_tuples) is not list:
            logger.debug("No Net Flows")
            return pan.DataFrame()

        else:
            net_dict = iof.nested_dicts(2)
            # for each tuple 
            for tuple in net_tuples:
                minuend_name = tuple[0]
                minuend_io = tuple[1].lower()
                subtrahend_name = tuple[2]
                subtrahend_io = tuple[3].lower()
                difference_name = f"{minuend_name} - {subtrahend_name}"

                for m_s, name, io in (['minuend', minuend_name, minuend_io],
                                      ['subtrahend', subtrahend_name, subtrahend_io]):

                    qty = 0

                    if io[0] in ["i", "o"]:
                        if name in io_dicts[io]:
                            qty = io_dicts[io][name]
                    elif io[0:5] == "agg_i":
                        if name in aggregated_df.index:
                            qty = aggregated_df.at[name, "inflows"]
                    elif io[0:5] == "agg_o":
                        if name in aggregated_df.index:
                            qty = aggregated_df.at[name, "outflows"]
                        pass
                    else:
                        raise ValueError("flow type must be i, o, agg_i, or agg_o")

                    net_dict[difference_name][m_s] = qty

                net_dict[difference_name]['difference'] = \
                    net_dict[difference_name]['minuend'] - net_dict[difference_name]['subtrahend']
                logger.debug(f"net flow written for {difference_name}")

            return iof.make_df(net_dict, drop_zero=False, T=True)

    # DIAGRAM SUBFUNCTIONS

    def clean_str_in_list(self, string, list):

        list = list.replace(f'{string}\n', '')
        list = list.replace(f'\n{string}', '')
        if '\n\n' in list:
            list = list.replace('\n\n', '\n')

        return list

    def connect_subgraphs(self, factory_diagram, factory_subgraphs):
        for dummy_i, c in self.connections_df.iterrows():
            product = c[dat.origin_product]
            origin_chain = c[dat.origin_chain]
            d_io = iof.clean_str(c[dat.dest_io][0])

            # line style for mass flows
            connection_color = dat.mass_color
            line_style = dat.mass_style

            # line style energy flows
            if iof.is_energy(product):
                connection_color = dat.energy_color
                line_style = dat.energy_style

            # line style for recycled flows
            if dat.replace in c and type(c[dat.replace]) is str and c[dat.replace] not in dat.no_var:
                connection_color = dat.recycled_color  # recycled energy flows will still have energy line style
                product = product + "\n(recycled)"

            # determine connection ends
            if d_io == 'i':
                dest_chain = c[dat.dest_chain] + factory_subgraphs[c[dat.dest_chain]]['process_list'][0]['process'].name
            elif d_io == 'o':
                dest_chain = c[dat.dest_chain] + factory_subgraphs[c[dat.dest_chain]]['process_list'][-1][
                    'process'].name

            if dat.dest_unit in c:  # if there's a destination unit, get the process index in the process list and them the name from the process
                d_process_id_list = [u['process'].u_id for u in factory_subgraphs[c[dat.dest_chain]]['process_list']]
                if c[dat.dest_unit] in [u['process'].u_id for u in
                                        factory_subgraphs[c[dat.dest_chain]]['process_list']]:
                    d_unit_index = d_process_id_list.index(c[dat.dest_unit])
                    dest_chain = c[dat.dest_chain] + factory_subgraphs[c[dat.dest_chain]]['process_list'][d_unit_index][
                        'process'].name

            if c[dat.origin_unit] == dat.connect_all:
                origin_list = [c[dat.origin_chain] + p['process'].name for p in
                               factory_subgraphs[origin_chain]['process_list']]
            else:
                o_process_id_list = [u['process'].u_id for u in factory_subgraphs[c[dat.origin_chain]]['process_list']]
                o_unit_index = o_process_id_list.index(c[dat.origin_unit])
                origin_list = [
                    c[dat.origin_chain] + factory_subgraphs[c[dat.origin_chain]]['process_list'][o_unit_index][
                        'process'].name]

            # draw connection
            for origin in origin_list:
                if d_io == 'i':
                    factory_diagram.edge(origin, dest_chain, label=product, color=connection_color,
                                         fontcolor=connection_color, style=line_style)
                elif d_io == 'o':
                    factory_diagram.edge(dest_chain, origin, label=product, color=connection_color,
                                         fontcolor=connection_color, style=line_style)

        return factory_diagram

    def add_flows_to_graph(self, flows, io, chain, process, io_diagram, factory_diagram, ):
        if flows and not flows.isspace():
            io_diagram.node(chain + process + flows, label=flows)

            if io == 'o':
                factory_diagram.edge(chain + process, chain + process + flows, color=dat.mass_color)
            else:
                factory_diagram.edge(chain + process + flows, chain + process, color=dat.mass_color)

        return io_diagram, factory_diagram
