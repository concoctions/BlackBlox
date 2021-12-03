# -*- coding: utf-8 -*-
""" Industry class
"""

from collections import defaultdict
from typing import List

import blackblox.calculators as calc
import blackblox.dataconfig as dat
import blackblox.factory as fac
import blackblox.io_functions as iof
from blackblox.bb_log import get_logger
from blackblox.frames import df_unit_library


logger = get_logger("Industry")


class Industry:
    """
    Industries are made up of one or more factories, and are balanced on one or more
    factory products. Factories within an industry can run with different scenario
    data. Industries can change over time.

    Args:
        factory_file (str): Location of spreadsheet containing factory list data, 
            and default location of production scenario data
        factory_list_sheet (str/None): name of sheet in workbook  with list of
            factories in the industry
            (Defaults to None)
        name (str): Name of Industry
            (Defaults to 'Industry')

    Attributes:
        name (str): Name of Industry
        factory_file (str): defualt location of factory production data
        factories_df (DataFrame): DataFrame of data about factories in the Industry
            including their name, the location of the spreadsheet containing their
            data, and the sheet names for their list of chains and connections
        product_list (set[str]): list of unique main output products of the factories
        factory_dict (dict): dictionary with the factory names, main products
            and Fac.Factory objects

    """

    def __init__(self, factory_list_file, factory_list_sheet=None, name='Industry', outdir=None,
                 units_df=df_unit_library, units_df_basedir=dat.bbcfg.paths.unit_process_library_file.parent,
                 **kwargs):
        self.name = name
        self.outdir = (outdir if outdir else dat.bbcfg.paths.path_outdir) / f'{dat.bbcfg.timestamp_str}__industry_{self.name}'
        self.factory_file = factory_list_file
        self.factories_df = iof.make_df(factory_list_file, factory_list_sheet, index=None)
        self.product_list = None
        self.factory_dict = None
        self.units_df = units_df
        self.units_df_basedir = units_df_basedir

    def build(self):
        """ generates the factory, chain, and process objects in the industry
        """
        logger.debug(f"initializing industry for {self.name}")

        factory_dict = defaultdict(dict)
        product_list = set()

        for i, f in self.factories_df.iterrows():
            name = f[dat.bbcfg.columns.factory_name]

            if dat.bbcfg.columns.factory_name in self.factories_df:
                f_chains_file_rel = f[dat.bbcfg.columns.factory_filepath]
                f_connections_file_rel = None if f[dat.bbcfg.columns.factory_filepath] in dat.bbcfg.no_var else f[dat.bbcfg.columns.factory_filepath]
            else:
                f_chains_file_rel = f[dat.bbcfg.columns.f_chain_list_file]
                f_connections_file_rel = f[dat.bbcfg.columns.f_connections_file]

            f_chains_file = self.units_df_basedir / f_chains_file_rel
            f_connections_file = self.units_df_basedir / f_connections_file_rel

            f_chains_sheet = iof.check_for_col(self.factories_df, dat.bbcfg.columns.f_chains_sheet, i)
            f_connections_sheet = iof.check_for_col(self.factories_df, dat.bbcfg.columns.f_connections_sheet, i)

            factory = fac.Factory(
                chain_list_file=f_chains_file,
                connections_file=f_connections_file,
                chain_list_sheet=f_chains_sheet,
                connections_sheet=f_connections_sheet,
                name=name,
                units_df=self.units_df,
                units_df_basedir=self.units_df_basedir,
            )

            factory_dict[name] = dict(
                factory=factory,
                product=factory.main_product,
                name=name,
            )

            product_list.add(factory.main_product)

            self.factory_dict = factory_dict
            self.product_list = product_list

    def balance(self, production_data_file=None, production_data_sheet=None,
                upstream_outflows=False, upstream_inflows=False,
                aggregate_flows=False, mass_energy=True,
                energy_flows=dat.bbcfg.energy_flows, force_scenario=None,
                write_to_xls=True, outdir=None, subfolder=True,
                foldertime=True, file_id='', diagrams=True, **kwargs):
        """Balances an industry using one scenario for each factory.

        Args:
            production_data_file (str/None): location of per-factory production 
                tabular data. If None, uses self.factory_file.
                (Defaults to None)
            production_data_sheet (str/None): name of sheet in a workbook where
                the production tabular data is. None if not an Excel file or
                the first sheet in the workbook.
                (Defaults to None)
            mass_energy (bool): Whether to seperate mass and energy flows in the
                output DataFrames.
                (Defaults to True)
            energy_flows (list): List of identifiers of what is an energy flow
                (Defaults to dat.bbcfg.energy_flows)
            force_scenario (str/None): Name of scenario to use for each factory,
                overriding the scenario specified in the production data
                (Defaults to None)
            write_to_xls (bool): Whether to output the data to file
                (Defaults to True)
            outdir (str): File output directory 
                (Defaults to dat.bbcfg.paths.path_outdir)
            subfolder (bool): If True, uses the industry name as a subfolder
                of the output directory.
                (Defaults to True)
            foldertime (bool): If True, uses the current timestamp in the output
                directory name. 
                (Defaults to True)
            file_id (str): Additional text to add to file names
                (Defaults to True)
            diagrams (bool): If True, includes factory and chain diagrams in the
                output files

        """
        logger.debug(f"attempting to balance {self.name}industry")

        outdir = outdir if outdir else self.outdir

        if self.factory_dict is None:
            self.build()

        # build full filename
        if subfolder is True:
            subfolder = self.name

        # outdir = iof.build_filedir(outdir, subfolder=subfolder,
        #                                 file_id_list=[file_id],
        #                                 time=foldertime)

        # get information about production at each factory in the industry
        if production_data_file is None and production_data_sheet is None:
            raise Exception("Neither data file path nor data sheet provided")
        elif production_data_file is None:
            production_data_file = self.factory_file

        product_df = iof.make_df(production_data_file, sheet=production_data_sheet)
        f_production_dict = defaultdict(dict)

        fractions = defaultdict(
            float)  # dictionary of products specified by relative production, rather than absolte production
        product_scenario = defaultdict(float)

        io_dicts = iof.nested_dicts(3, float)

        # get production scenario data
        for i, f in product_df.iterrows():
            product = f[dat.bbcfg.columns.f_product]
            if iof.clean_str(i) in dat.bbcfg.all_factories:  # recognizes that this production total is for all factories
                if product not in dat.bbcfg.no_var:
                    fractions[product] = f[dat.bbcfg.columns.f_product_qty]  # industry-wide product total
                if isinstance(f[dat.bbcfg.columns.f_scenario], str) and iof.clean_str(f[dat.bbcfg.columns.f_scenario]) not in dat.bbcfg.no_var:
                    product_scenario[product] = f[dat.bbcfg.columns.f_scenario]  # scenario for all factories producing that product
            else:
                if product in fractions:  # product qty should be decimal fraction of total
                    calc.check_qty(f[dat.bbcfg.columns.f_product_qty], fraction=True)
                    product_qty = f[dat.bbcfg.columns.f_product_qty] * fractions[product]
                else:
                    product_qty = f[dat.bbcfg.columns.f_product_qty]

                if force_scenario is not None:
                    scenario = force_scenario
                else:
                    if product in product_scenario:
                        scenario = product_scenario[product]
                    else:
                        scenario = f[dat.bbcfg.columns.f_scenario]

                f_production_dict[i] = dict(product_qty=product_qty,
                                            scenario=scenario,
                                            write_to_xls=write_to_xls,
                                            outdir=outdir / 'factories',
                                            upstream_outflows=upstream_outflows,
                                            upstream_inflows=upstream_inflows,
                                            aggregate_flows=aggregate_flows,
                                            )

        for f in f_production_dict:
            factory = self.factory_dict[f]['factory']
            f_kwargs = f_production_dict[f]
            io_dicts['inflows'][f], io_dicts['outflows'][f], dummy_agg, dummy_net = factory.balance(**f_kwargs)

            if diagrams:
                factory.diagram(outdir=outdir / 'pfd')

        totals_in = defaultdict(float)
        totals_out = defaultdict(float)

        for factory in io_dicts['inflows']:
            for substance, qty in io_dicts['inflows'][factory].items():
                totals_in[substance] += qty
            for substance, qty in io_dicts['outflows'][factory].items():
                totals_out[substance] += qty

        io_dicts['inflows']['industry totals'] = totals_in
        io_dicts['outflows']['industry totals'] = totals_out

        if write_to_xls is True:
            filename = f'i_{self.name}_{file_id}_{dat.bbcfg.timestamp_str}'

            meta_df = iof.metadata_df(user=dat.bbcfg.user,
                                      name=self.name,
                                      level="Industry",
                                      scenario="--",
                                      product=', '.join(self.product_list),
                                      product_qty="--",
                                      energy_flows=energy_flows)

            inflows_df = iof.make_df(io_dicts['inflows'], drop_zero=True)
            inflows_df = iof.mass_energy_df(inflows_df, aggregate_consumed=True)
            outflows_df = iof.make_df(io_dicts['outflows'], drop_zero=True)
            outflows_df = iof.mass_energy_df(outflows_df, aggregate_consumed=True)

            df_list = [meta_df, inflows_df, outflows_df]
            sheet_list = ["meta", f'{self.name} inflows', f'{self.name} outflows']

            iof.write_to_xls(df_list, sheet_list=sheet_list,
                             outdir=outdir, filename=filename)

        logger.debug(f"successfully balanced {self.name}industry")

        return io_dicts  # io_dicts[flow i_o][factory][substance] = qty

    def run_scenarios(self, scenario_list: List[str], products_data=None, products_sheet=None,
                      write_to_xls=True, outdir=None, file_id='', diagrams=False,
                      upstream_outflows=False, upstream_inflows=False, aggregate_flows=False, **kwargs):
        """Balances an industry using one scenario for each factory.

        Args:
            scenario_list: List of scenarios to use to balance industry
                on, forcing that scenario for each factory in the industry
            products_data (str/None): location of per-factory production 
                tabular data. If None, uses self.factory_file.
                (Defaults to None)
            products_sheet (str/None): name of sheet in a workbook where
                the production tabular data is. None if not an Excel file or
                the first sheet in the workbook.
                (Defaults to None)
            write_to_xls (bool): Whether to output the data to file
                (Defaults to True)
            outdir (str): File output directory 
                (Defaults to dat.bbcfg.paths.path_outdir)
            file_id (str): Additional text to add to file names
                (Defaults to True)
            diagrams (bool): If True, includes factory and chain diagrams in the
                output files

        """

        outdir_base = outdir if outdir else self.outdir
        outdir = iof.build_filedir(
            outdir_base, subfolder=self.name, file_id_list=['multiscenario', file_id], time=True)

        scenario_dict = iof.nested_dicts(4)

        for scenario in scenario_list:
            s_dict = self.balance(production_data_file=products_data,
                                  production_data_sheet=products_sheet,
                                  force_scenario=scenario,
                                  write_to_xls=write_to_xls,
                                  outdir=outdir / scenario,
                                  file_id=f'{file_id}_{scenario}',
                                  diagrams=diagrams,
                                  upstream_outflows=False,
                                  upstream_inflows=False,
                                  aggregate_flows=False, )
            scenario_dict['i'][scenario] = s_dict['inflows']['industry totals']
            scenario_dict['o'][scenario] = s_dict['outflows']['industry totals']

        inflows_df = iof.make_df(scenario_dict['i'], drop_zero=True)
        inflows_df = iof.mass_energy_df(inflows_df, aggregate_consumed=True)
        outflows_df = iof.make_df(scenario_dict['o'], drop_zero=True)
        outflows_df = iof.mass_energy_df(outflows_df, aggregate_consumed=True)

        meta_df = iof.metadata_df(user=dat.bbcfg.user,
                                  name=self.name,
                                  level="Industry",
                                  scenario=" ,".join(scenario_list),
                                  product=" ,".join(self.product_list),
                                  product_qty="--",
                                  energy_flows=dat.bbcfg.energy_flows)

        if write_to_xls is True:
            iof.write_to_xls(df_or_df_list=[meta_df, inflows_df, outflows_df],
                             sheet_list=["meta", "inflows", "outflows"],
                             outdir=outdir,
                             filename=f'{self.name}_multiscenario_{dat.bbcfg.timestamp_str}')

    def evolve(self, start_data=None, start_sheet=None, end_data=None, end_sheet=None,
               start_step=0, end_step=1, mass_energy=True, energy_flows=dat.bbcfg.energy_flows,
               write_to_xls=True, outdir=None, file_id='', diagrams=True, graph_outflows=False,
               graph_inflows=False, upstream_outflows=False, upstream_inflows=False, aggregate_flows=False, **kwargs):
        """Calculates timestep and cumulative inflows and outflows of an industry
        using a specified starting scenario and end scenario
        
        Args:
            start_data (str/None): location of production tabular data file for
                start step. If none, uses self.factory_file
            start_sheet (str/None): sheet name of start step production data
            end_data (str/None): location of production tabular data file for
                end step. If none, uses self.factory_file
            end_sheet (str/None): sheet name of end step production data
            start_step (int): numerical index of start step (e.g. start year) that
                corresponds to the production data in start_data
            end_step (int): numerical index of end step (e.g. end year) that
                corresponds to the production data in end_data
            mass_energy (bool):
            energy_flows (list):
            write_to_xls (bool):
            outdir (str):
            file_id (bool):
            diagrams (bool):
            graph_outflows (list/bool): list of outflows to graph with their
                change over time, with one line for each factory
            graph_inflows (list/bool): list of inflows to graph with their
                change over time, with one line for each factory
        """

        outdir_base = outdir if outdir else self.outdir
        outdir = iof.build_filedir(
            outdir_base, subfolder=self.name, file_id_list=['evolve', start_step, end_step, file_id], time=True)

        kwargs = dict(write_to_xls=write_to_xls,
                      diagrams=diagrams,
                      file_id=file_id,
                      mass_energy=mass_energy,
                      energy_flows=energy_flows,
                      subfolder=None,
                      foldertime=False,
                      upstream_outflows=upstream_outflows,
                      upstream_inflows=upstream_inflows,
                      aggregate_flows=aggregate_flows)

        start_io = self.balance(production_data_file=start_data,
                                production_data_sheet=start_sheet,
                                outdir=outdir / f'start_{start_step}',
                                **kwargs)

        end_io = self.balance(production_data_file=end_data,
                              production_data_sheet=end_sheet,
                              outdir=outdir / f'end_{end_step}',
                              **kwargs)

        # io_dicts are in the form of:
        # io_dict['factory name' or 'industry totals']['inflows' or 'outflows']['substance'] = qty

        # harmonize start_io and end_io dict keys:

        to_harmonize = [(start_io, end_io), (end_io, start_io)]

        for pair in to_harmonize:
            for flow in pair[0]:
                for factory in pair[0][flow]:
                    for substance in pair[1][flow][factory]:
                        if substance not in pair[0][flow][factory]:
                            pair[0][flow][factory][substance] = 0

        stepcount = end_step - start_step
        slope_dict = iof.nested_dicts(3)

        for flow in end_io:
            for factory in end_io[flow]:
                for substance in end_io[flow][factory]:
                    end_qty = end_io[flow][factory][substance]
                    start_qty = start_io[flow][factory][substance]
                    slope = ((end_qty - start_qty) / stepcount)  # m = (y-b)/x
                    slope_dict[flow][factory][substance] = slope

        annual_flows = iof.nested_dicts(4)  # [flow i_o][factory][substance][timestep] = float
        cumulative_dict = iof.nested_dicts(3)  # [flow i_o][factory][substance] = float

        for i in range(stepcount + 1):
            step = str(start_step + i)
            for flow in start_io:
                for factory in start_io[flow]:
                    for substance, qty in start_io[flow][factory].items():
                        slope = slope_dict[flow][factory][substance]
                        step_qty = qty + (i * slope)  # y = mx + b
                        annual_flows[flow][factory][substance][step] = step_qty
                        cumulative_dict[flow][factory][substance] += step_qty

        if write_to_xls is True:

            filename = (f'i_{self.name}_{start_step}-{end_step}_{file_id}'
                        f'_{dat.bbcfg.timestamp_str}')

            cumulative_infows_df = iof.make_df(cumulative_dict['inflows'], drop_zero=True)
            cumulative_infows_df = iof.mass_energy_df(cumulative_infows_df)
            cumulative_outflows_df = iof.make_df(cumulative_dict['outflows'], drop_zero=True)
            cumulative_outflows_df = iof.mass_energy_df(cumulative_outflows_df)

            meta_df = iof.metadata_df(user=dat.bbcfg.user, name=self.name,
                                      level="Industry", scenario="n/a", product=" ,".join(self.product_list),
                                      product_qty="n/a", energy_flows=dat.bbcfg.energy_flows)

            df_list = [meta_df, cumulative_infows_df, cumulative_outflows_df]
            sheet_list = ["meta", "cum inflows", "cum outflows"]
            df_dict = iof.nested_dicts(2)
            # df_dict['i']['culmulative'] = cumulative_infows_df
            # df_dict['o']['culmulative'] = cumulative_outflows_df

            for flow in annual_flows:
                for factory in annual_flows[flow]:
                    df = iof.make_df(annual_flows[flow][factory], drop_zero=False, sort=True)
                    sheet_name = f'{factory} {flow}'
                    df_dict[flow[0]][factory] = df
                    if 'total' in factory:
                        df_list.insert(1, df)
                        sheet_list.insert(1, sheet_name)
                    else:
                        df_list.append(df)
                        sheet_list.append(sheet_name)

            iof.write_to_xls(df_list, sheet_list=sheet_list,
                             outdir=outdir, filename=filename)

        if type(graph_outflows) is list:
            for flow in graph_outflows:
                iof.plot_annual_flows(df_dict['o'], flow, outdir)

        if type(graph_inflows) is list:
            for flow in graph_inflows:
                iof.plot_annual_flows(df_dict['i'], flow, outdir)

        return annual_flows, cumulative_dict

    def evolve_multistep(self, steps=None, production_data_files=None, step_sheets=None,
                         file_id='', outdir=None, write_to_xls=True,
                         graph_inflows=False, graph_outflows=False,
                         upstream_outflows=False, upstream_inflows=False, aggregate_flows=False, **kwargs):
        """the same as evolve, but takes a list of an arbitrary number of steps
        Args:
            steps (list[int]): list of numerical time steps
            production_data_files (list): list of file location of production data for
                each time step (in step order). If None, assumes self.factory_file
                for each step
            step_sheets (list): List of sheets in workbooks for production data
                for each time step. If None, assumes None for each step.
            outdir (str):
            write_to_xls (bool):
            graph_outflows (list/bool): list of outflows to graph with their
                change over time, with one line for each factory
            graph_inflows (list/bool): list of inflows to graph with their
                change over time, with one line for each factory
        """

        outdir_base = outdir if outdir else self.outdir
        outdir = iof.build_filedir(
            outdir_base, subfolder=self.name, file_id_list=['evolve_multistep', steps[0], steps[-1], file_id], time=True)

        step_annual_flows = []
        step_cumulative_flows = []

        if len(steps) < 2:
            raise ValueError("Too few steps were specified")
        elif len(steps) == 2:
            two_step = True
            logger.debug("only two steps given; only performing a single-evolve function")
        else:
            two_step = False

        if step_sheets is None:
            step_sheets = [None for i in range(len(steps))]

        if production_data_files is None:
            production_data_files = [None for i in range(len(steps))]

        for i, step in enumerate(steps):
            if i == 0:
                pass
            else:
                s_kwargs = dict(start_data=production_data_files[i - 1],
                                start_sheet=step_sheets[i - 1],
                                end_data=production_data_files[i],
                                end_sheet=step_sheets[i],
                                start_step=prev_step,
                                end_step=step,
                                mass_energy=True,
                                energy_flows=dat.bbcfg.energy_flows,
                                write_to_xls=write_to_xls,
                                outdir=outdir / f'{prev_step}_{step}',
                                diagrams=False,
                                upstream_outflows=upstream_outflows,
                                upstream_inflows=upstream_inflows,
                                aggregate_flows=aggregate_flows)

                annual, cumulative = self.evolve(**s_kwargs)
                if two_step is True:
                    return annual, cumulative
                step_annual_flows.append(annual)
                step_cumulative_flows.append(cumulative)
            prev_step = step

        merged_annual_flows = iof.nested_dicts(4)  # [flow i_o][factory][substance][timestep] = float
        for step_dict in step_annual_flows:
            for i_o, factory_dict in step_dict.items():
                for factory, substance_dict in factory_dict.items():
                    for substance, timestep_dict in substance_dict.items():
                        for timestep, qty in timestep_dict.items():
                            merged_annual_flows[i_o][factory][substance][timestep] = qty

        merged_cumulative_flows = iof.nested_dicts(3)  # [flow i_o][factory][substance] = float
        for step_dict in step_cumulative_flows:
            for i_o, factory_dict in step_dict.items():
                for factory, substance_dict in factory_dict.items():
                    for substance, qty in substance_dict.items():
                        merged_cumulative_flows[i_o][factory][substance] = qty

        if write_to_xls is True:

            filename = (f'i_{self.name}_{steps[0]}-{steps[-1]}_{file_id}'
                        f'_{dat.bbcfg.timestamp_str}')

            cumulative_infows_df = iof.make_df(merged_cumulative_flows['inflows'], drop_zero=True)
            cumulative_infows_df = iof.mass_energy_df(cumulative_infows_df, aggregate_consumed=True)
            cumulative_outflows_df = iof.make_df(merged_cumulative_flows['outflows'], drop_zero=True)
            cumulative_outflows_df = iof.mass_energy_df(cumulative_outflows_df, aggregate_consumed=True)

            meta_df = iof.metadata_df(user=dat.bbcfg.user, name=self.name,
                                      level="Industry", scenario="n/a", product=" ,".join(self.product_list),
                                      product_qty="n/a", energy_flows=dat.bbcfg.energy_flows)

            df_list = [meta_df, cumulative_infows_df, cumulative_outflows_df]
            sheet_list = ["meta", "cum inflows", "cum outflows"]
            df_dict = iof.nested_dicts(2)
            # df_dict['i']['culmulative'] = cumulative_infows_df
            # df_dict['o']['culmulative'] = cumulative_outflows_df

            for flow in merged_annual_flows:
                for factory in merged_annual_flows[flow]:
                    df = iof.make_df(merged_annual_flows[flow][factory], drop_zero=False, sort=True)
                    sheet_name = f'{factory} {flow}'
                    df_dict[flow[0]][factory] = df
                    if 'total' in factory:
                        df_list.insert(1, df)
                        sheet_list.insert(1, sheet_name)
                    else:
                        df_list.append(df)
                        sheet_list.append(sheet_name)

            iof.write_to_xls(df_list, sheet_list=sheet_list,
                             outdir=outdir, filename=filename)

        if type(graph_outflows) is list:
            for flow in graph_outflows:
                iof.plot_annual_flows(df_dict['o'], flow, outdir)

        if type(graph_inflows) is list:
            for flow in graph_inflows:
                iof.plot_annual_flows(df_dict['i'], flow, outdir)

        return merged_annual_flows, merged_cumulative_flows
