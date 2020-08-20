# -*- coding: utf-8 -*-
""" Unit process class

This module contains the Unit Process class, which fundamenta building block of
blackblox.py



The primary function of the unit process class, Balance, calculates all the 
inflows and outflows of the unit proces based on a single specified flow quantity.

Module Outline:

- import statements and logger
- module variable: df_units_library (dataframe)
- class: UnitProcess
    - class function: Balance
    - class function: recycle_1to1
    - class function: recycle_energy_replacing_fuel

    subfunctions used in UnitProcess.balance():
    - class subfunction: check_io
    - class subfunction: check_product
    - class subfunction: make_io_dicts
    - class subfunction: check_attempt
    - class subfunction: check_substance
    - class subfunction: check_lookup
    - class subfunction: check_calc
"""

from collections import defaultdict
from copy import copy
from math import isnan
import numpy as np
from datetime import datetime

from blackblox.bb_log import get_logger
import blackblox.io_functions as iof
import blackblox.dataconfig as dat
import blackblox.calculators  as calc
from blackblox.frames import df_unit_library, lookup_var_dict

logger = get_logger("Unit Process")



class UnitProcess:
    """UnitProcess(u_id, display_name=False, var_df=False, calc_df=False, units_df=df_unit_library)
    Unit processes have inflows and outflows with defined relationships.

    Each unit process has a set inflows and outflows, whose relationships 
    are specified in a calculations table. These relationships must be specified so
    that the provision of the quantity of one inflow or outflow is sufficient to
    balance the entire process. 

    The numeric values of the relationships are specified in a separate variables 
    table, which can contain many different scenarios of variables for the same unit 
    process.

    Args:
        u_id (str): unique ID of the process
        display_name (str/bool): the display name used for output of the process.
            If False, fetches data from df_unit_library
        var_df (str/dataframe/bool): Dataframe or filepath of
            the tabular variable data to use when balancing the unit process. 
            If False, fetches data location from df_unit_library
            (Defaults to False)
        calc_df (str/dataframe/bool):  ataframe or filepath of
            the tabular relationship data to use when balancing the unit process. 
            If False, fetches data location from df_unit_library
            (Defaults to False)
        units_df (dataframe): Unit process library data frame
            (Defaults to df_unit_library)

    Attributes:
        u_id (str): unique ID of the process
        display_name (str): Name of process
        var_df (dataframe): Dataframe of relationship variable values
            indexed by scenario name.
        calc_df (dataframe): Dataframe of relationships between unit
            process flows.
        default_product (str): The primary "product" flow of the unit
            process. Derived from units_df.
        default_io (str): Whether the primary product is an inflow
            or an outflow. Derived from units_df.
        inflows (set[str]): List of inflows to the unit process. Derived
            from calc_df.
        outflows (set[str]): List of outflows to the unit process. Derived
            from calc_df.
    """

    def __init__(self, 
                 u_id,
                 display_name=False, 
                 var_df=False, 
                 calc_df=False, 
                 units_df=df_unit_library):

        logger.info(f"creating unit process object for {u_id} ({display_name})")

        self.u_id = u_id

        if display_name is not False:
            self.name = display_name
        elif dat.unit_name in units_df:
            self.name = units_df.at[u_id, dat.unit_name]
        else:
            self.name = u_id

        if var_df is not False:
            self.var_df = iof.make_df(var_df)
        else:
            v_sheet = iof.check_for_col(units_df, dat.var_sheetname, u_id)
            self.var_df = iof.make_df(units_df.at[u_id, dat.var_filepath], 
                                      sheet=v_sheet, lower_cols=True, fillna=True)

        if calc_df is not False:
            self.calc_df = calc_df
        else:
            c_sheet = iof.check_for_col(units_df, dat.calc_sheetname, u_id)
            self.calc_df = iof.make_df(units_df.at[u_id, dat.calc_filepath], 
                                       sheet=c_sheet, 
                                       index=None)


       
        self.default_product = iof.check_for_col(units_df, dat.unit_product, u_id)  # use default value if available, otherwise none
        self.default_io = iof.check_for_col(units_df, dat.unit_product_io, u_id)  # use default value if available, otherwise none
        
        self.inflows = set() 
        self.outflows = set() 
        self.mass_inflows = set() 
        self.mass_outflows = set() 
        self.energy_inflows = set() 
        self.energy_outflows = set() 
        
        for i in self.calc_df.index: 
            if type(self.calc_df.at[i, dat.known]) is str: # removes blank rows
                products = [ (self.calc_df.at[i, dat.known], 
                    iof.clean_str(self.calc_df.at[i, dat.known_io][0])),
                        (self.calc_df.at[i, dat.unknown],
                        iof.clean_str(self.calc_df.at[i, dat.unknown_io][0]))]

            for product, i_o in products:
                if not product.startswith(dat.consumed_indicator): #ignores flows that are specified as balance items
                    if i_o in ['i', 'c']:
                        self.inflows.add(product)
                        if iof.is_energy(product): #sorts based on dat.energy_flows
                            self.energy_inflows.add(product)
                        else:
                            self.mass_inflows.add(product)
                    elif i_o in ['o', 'e']:
                        self.outflows.add(product)
                        if iof.is_energy(product):
                            self.energy_outflows.add(product)
                        else:
                            self.mass_outflows.add(product)

                    if 'combustion' in self.calc_df.at[i, dat.calc_type]: #adds combustion emissions and balancing energy flows
                        for emission in dat.default_emissions:
                            self.outflows.add(emission)
                            self.mass_outflows.add(emission)
                        self.energy_inflows.add(f"energy embodied in fuels")
                        self.energy_outflows.add("waste heat")
            
 
    def balance(self, 
                qty=1.0, 
                product=False, 
                i_o=False, 
                scenario=dat.default_scenario,
                product_alt_name=False,
                balance_energy=True, 
                raise_imbalance=False,
                write_to_console=False):
        """balance(self, qty, product=False, i_o=False, scenario=dat.default_scenario, energy_flows=dat.energy_flows, balance_energy=True, raise_imbalance=False,)
        performs a mass (and/or energy) balance on the unit process.

        Calculates all inflows and outflows, using the specified relationships in
        the calculations dataframe and the variable values for a scenario in the 
        variables dataframe.

        Note:
            If the inflow mass and outflow mass are imbalanced an error will
            be raised and/or a "UNKNOWN MASS" or  "UNKNOWN ENERGY " flow will 
            be added to the offending flow dictionary with the imbalance quantity.

        Args:
            qty (float): The quantity of the balancing flow
            product (str/bool): the inflow or outflow on which to balance 
                the calculations. If False, uses the default product, if specified.
                (Defaults to False)
            i_o (str): 'i' or 'o', depending on whether the specified
                product is an inflow (i) or outflow (o). If False, uses the 
                default product's location, if specified
                (Defaults to False)
            scenario (str): row index of var_df to use for the variables value,
                generally corresponding to the name of the scenario. If
                False, uses the default scenario index specified in 
                dataconfig.
                (Defaults to False)
            product_alt_name (str/bool): If string, uses this substance name
                in place of the substance name of the product for inflow
                and outflow dictonaries (and including lookups). Otherwise
                balances the unit process as normal.
                (Defaults to False)
            energy_flows (list[str]): If any substance name starts with
                or ends with a string on this list, the substance will not 
                be considered when performing the mass balance.
                Defaults to energy keyword list in dataconfig.
            balance_energy(bool): If true, checks for a balance of the flows
                with the specified energy prefix/suffix in energy_flows.
            raise_imbalance (bool): If True, the process will raise an 
                exception if the inflow and outflow masses and/or energies are 
                unbalanced. If False, will add a "UNKNOWN MASS" or "UNKNOWN 
                ENERGY" substance to the offended inflow or outflow dictionary.
                Defaults to False.

        Returns:
            Defaultdict of inflows with substance names as keys and quantities as values
            Defaultdict of outflows with substance names as keys and quantities as values.
        """

        i_o = self.check_io(i_o)
        product_qty = qty
        
        if scenario not in self.var_df.index.values:
            raise Exception(f'{self.name.upper()}: {scenario} not found in variables file')

        product = self.check_product(product)
        if product in lookup_var_dict: 
            lookup_product_key = product 
            product = self.var_df.at[scenario, lookup_var_dict[product]['lookup_var']]  # get product name from var_df, at variable specified in lookup_var_dict
        else:
            lookup_product_key = False

        # create flow dictionaries and seed with product qty
        io_dicts = self.make_io_dicts(product, product_qty, i_o, product_alt_name)

        calc_df = self.calc_df
        logger.info(f"{self.name.upper()}: Attempting to balance on {qty} of {product} (different name from origin: {product_alt_name}) ({i_o}) using {scenario} variables")

        i = 0
        attempt = 0

        while len(calc_df) > 0:
            i = self.check_attempt(i, attempt, calc_df)     
    
            # get flow names and locations
            logger.debug("if you get an error here, verify value types the var file (e.g. string, float") #I don't remember exactly how this applies
            known_substance, known_proxy, known_lookup = self.check_substance(calc_df.at[i, dat.known], scenario, product, product_alt_name, lookup_product_key)
            unknown_substance, unknown_proxy, unknown_lookup = self.check_substance(calc_df.at[i, dat.unknown], scenario, product, product_alt_name, lookup_product_key)
            known_io = iof.clean_str(calc_df.at[i, dat.known_io][0])
            unknown_io = iof.clean_str(calc_df.at[i, dat.unknown_io][0]) 

            lookup_df = self.check_lookup(known_lookup, unknown_lookup)
                
            calc_type = iof.clean_str(calc_df.at[i, dat.calc_type])
            skip, invert, known2_qty, known2_proxy = self.check_calc(i, calc_type, calc_df, scenario, known_substance, known_io, unknown_substance, unknown_io, io_dicts)

            logger.debug(f"{self.name.upper()}: current index: {i}, current product: {known_substance}")
            
            var = self.check_var(calc_df.at[i, dat.calc_var], calc_type, scenario)
            
            if skip is True:
                i += 1
                attempt += 1
                logger.debug(f"{self.name.upper()}: neither {known_substance} nor {unknown_substance} found, skipping for now")
                continue

            # inverts when original unknown_substance is available but qty of known_substance is not
            if invert is True: 
                known_substance, unknown_substance = unknown_substance, known_substance
                known_io, unknown_io = unknown_io, known_io
                known_proxy, unknown_proxy = unknown_proxy, known_proxy
                logger.debug(f"{self.name.upper()}: {known_substance} not found, but {unknown_substance} found. Inverting calculations")

            qty_known = io_dicts[known_io][known_substance]
            
            # set kwargs for calculation
            kwargs = dict(qty=calc.no_nan(qty_known), 
                          var=calc.no_nan(var), 
                          known_substance=known_proxy, 
                          unknown_substance=unknown_proxy,
                          known2_substance = known2_proxy,
                          qty2 = calc.no_nan(known2_qty),
                          invert=invert, 
                          emissions_dict=io_dicts['e'],
                          inflows_dict=io_dicts['c'],
                          lookup_df = lookup_df)
            kwargs = {**kwargs, **calc.calcs_dict[calc_type]['kwargs']} # add additional kwargs based on specified calc type
            
            # calculate
            logger.debug(f"{self.name.upper()}: Attempting {calc_type} calculation for {unknown_substance} using {qty_known} of {known_substance}")
            qty_calculated = calc.calcs_dict[calc_type]['function'](**kwargs)
            qty_calculated = calc.no_nan(qty_calculated)
            if qty_calculated < 0:
                qty_calculated = round(qty_calculated, dat.float_tol) #to avoid propogating floating point errors
            calc.check_qty(qty_calculated)
            
            # write qty calculated to dictionary
            if unknown_io in ['c', 'e']:
                io_dicts[unknown_io][unknown_substance] += qty_calculated
            elif unknown_io == 'd':
                pass
            else:
                io_dicts[unknown_io][unknown_substance] = qty_calculated

            # remove row of completed calculation from calc_df
            calc_df = calc_df.drop(i)
            calc_df = calc_df.reset_index(drop=True)
            attempt = 0
            logger.debug(f"{self.name.upper()}: {qty_calculated} of {unknown_substance} calculated. {len(calc_df)} calculations remaining.")

        # After processing all rows in calc_df
        for substance, qty in io_dicts['e'].items(): #adds emissions dictionary to outflow dictionary
            io_dicts['o'][substance] += qty
        for substance, qty in io_dicts['c'].items(): #adds co-inflows dictionary to inflows dictionary
            io_dicts['i'][substance] += qty

        # check if inflows and outflows balance
        logger.debug(f"{self.name.upper()}: Balancing mass flows")
        total_mass_in, total_mass_out = calc.check_balance(io_dicts['i'], io_dicts['o'],
                                                 raise_imbalance=raise_imbalance, 
                                                 ignore_flows=dat.energy_flows)

        if total_mass_in > total_mass_out:
            io_dicts['o']['UNKNOWN-mass'] = total_mass_in - total_mass_out
            logger.info(f"{self.name.upper()}: mass imbalance found {total_mass_in - total_mass_out} of UNKNOWN MASS added to outflows")
        elif total_mass_out > total_mass_in:
            io_dicts['i']['UNKNOWN-mass'] = total_mass_out - total_mass_in
            logger.info(f"{self.name.upper()}:mass imbalance found {total_mass_out - total_mass_in} of UNKNOWN MASS added to inflows")

        if balance_energy is True:
            logger.debug(f"{self.name.upper()}: Balancing energy flows")
            total_energy_in, total_energy_out = calc.check_balance(io_dicts['i'], io_dicts['o'],
                                                 raise_imbalance=raise_imbalance, 
                                                 ignore_flows=[],
                                                 only_these_flows=dat.energy_flows)
            if total_energy_in > total_energy_out:
                io_dicts['o']['UNKNOWN-energy'] = total_energy_in - total_energy_out
                logger.info(f"{self.name.upper()}: energy imbalance found {total_energy_in - total_energy_out} of UNKOWN ENERGY added to outflows")
            elif total_mass_out > total_mass_in:
                io_dicts['i']['UNKNOWN-energy'] = total_energy_out - total_energy_in
                logger.info(f"{self.name.upper()}:energy imbalance found {total_energy_in - total_energy_out} of UNKOWN ENERGY added to inflows")

        logger.info(f"{self.name} process balanced on {qty} of {product}")

        if write_to_console is True:
            self.write_to_console(io_dicts, scenario, product_qty, product)

        return io_dicts['i'], io_dicts['o']


    def run_scenarios(self, scenario_list=[], qty=1.0, product=False, i_o=False, product_alt_name=False, 
        balance_energy=True, raise_imbalance=False, write_to_xls=True, write_to_console=False):
        """Runs UnitProcess.balance over multiple scenarions of varaibles. Outputs to Excel.

        """
        
        iof.check_type(scenario_list, is_type=[list], not_not=True)
        scenario_dict = iof.nested_dicts(3)

        if product is False:
            product = self.default_product
        
        # balance UnitProcess on each scenario of variable values
        for scenario in scenario_list:
            u_in, u_out = self.balance(qty=qty, 
                                               product=product,
                                               scenario=scenario,
                                               i_o=i_o,
                                               product_alt_name=product_alt_name,
                                               balance_energy=balance_energy, 
                                               raise_imbalance=raise_imbalance, 
                                               write_to_console=write_to_console)
            
            scenario_dict['i'][scenario] = u_in
            scenario_dict['o'][scenario] = u_out

        if write_to_xls is True or write_to_console is True:
            inflows_df = iof.mass_energy_df(scenario_dict['i'])
            outflows_df = iof.mass_energy_df(scenario_dict['o'])

        if write_to_xls is True:
            meta_df = iof.metadata_df(user=dat.user_data, 
                                        name=self.name, 
                                        level="Unit", 
                                        scenario=" ,".join(scenario_list), 
                                        product=product,
                                        product_qty=qty)

            dfs = [meta_df, inflows_df, outflows_df]
            sheets = ["meta", "inflows", "outflows"]

            iof.write_to_xls(df_or_df_list=dfs,
                                sheet_list=sheets, 
                                filename=f'{self.name}_u_multi_{datetime.now().strftime("%b%d_%H%M")}')

        
        if write_to_console is True:
            print(f"\n{str.upper(self.name)} balanced on {qty} of {product}.\n")
            print("\nINFLOWS\n", inflows_df)
            print("\nOUTFLOWS\n", outflows_df, "\n")
        
        return inflows_df, outflows_df

    
    def recycle_1to1(self, 
                       original_inflows_dict,
                       original_outflows_dict,
                       recycled_qty,
                       recycle_io,
                       recyclate_flow,
                       toBeReplaced_flow,
                       max_replace_fraction=1.0,
                       scenario=dat.default_scenario, 
                       write_to_console=False,
                       **kwargs):
    
        """Replaces a calculated flow within a unit process with another flow, either wholly or partially

        Args:
            original_inflows_dict (defaultdict): Dictionary of inflow quantities 
                from the orignal balancing of the unit process
            original_outflows_dict (defaultdict): Dictionary of outflow 
                quantities from the orignal balancing of the unit process
            recycled_qty (float): quantity of recycled flow
            recycle_io (str): "i" if the recycled flow is an inflow or "o" if 
                it is an outflow
            recyclate_flow (str): name of the recycled flow
            replaced_flow (str): name of the flow to be replaced by the recycled flow
            max_replace_fraction (float/none): the maximum percentage of the 
                original flow that the recycled flow is allowed to replace

        Returns:
            - *dictionary* of rebalanced inflows
            - *dictionary* of rebalanced outflows
            - *float* of the remaining quantity of the recycle stream
        """
        logger.info(f'{self.name.upper()}: attempting to replace {toBeReplaced_flow} with {recyclate_flow}')

        original_flows = dict(i=original_inflows_dict,
                              o=original_outflows_dict)
        rebalanced_flows = dict(i=copy(original_inflows_dict),
                                o=copy(original_outflows_dict))
    

        i_o =iof.clean_str(recycle_io[0])

        if i_o not in ['i', 'o']:
            raise KeyError(f'{i_o} is unknown flow location (Only inflows and outflows allowed for rebalanced processes')
        
        if toBeReplaced_flow in lookup_var_dict:
            toBeReplaced_flow = self.var_df.at[scenario, lookup_var_dict[toBeReplaced_flow]['lookup_var']] 
        if toBeReplaced_flow in calc.df_fuels:
            logger.info(f'{self.name.upper()}: WARNING! {toBeReplaced_flow} is a fuel. Combustion emissions will NOT be replaced. Use recycle_energy_replacing_fuel instead.')

        calc.check_qty(max_replace_fraction, fraction = True)

        replacable_qty = original_flows[i_o][toBeReplaced_flow] * max_replace_fraction
        unused_recyclate_qty = recycled_qty - replacable_qty

        if unused_recyclate_qty >= 0:
            used_recyclate_qty = recycled_qty - unused_recyclate_qty
            calc.check_qty(used_recyclate_qty)
        else:
            used_recyclate_qty = recycled_qty
            unused_recyclate_qty = 0

        rebalanced_flows[i_o][toBeReplaced_flow] -= used_recyclate_qty
        if rebalanced_flows[i_o][toBeReplaced_flow] <0:
            rebalanced_flows[i_o][toBeReplaced_flow] = round(rebalanced_flows[i_o][toBeReplaced_flow], dat.float_tol)
            calc.check_qty(rebalanced_flows[i_o][toBeReplaced_flow])
        rebalanced_flows[i_o][recyclate_flow] += used_recyclate_qty
        if rebalanced_flows[i_o][recyclate_flow] <0:
            rebalanced_flows[i_o][recyclate_flow] = round(rebalanced_flows[i_o][recyclate_flow], dat.float_tol)
            calc.check_qty(rebalanced_flows[i_o][recyclate_flow])

        calc.check_qty(unused_recyclate_qty)

        logger.info(f'{self.name.upper()}: {toBeReplaced_flow} replaced with {used_recyclate_qty} of {recyclate_flow}.')

        if write_to_console is True:
            self.write_to_console(rebalanced_flows, scenario, used_recyclate_qty, recyclate_flow, toBeReplaced_flow)       
       
        return rebalanced_flows['i'], rebalanced_flows['o'], unused_recyclate_qty


    def recycle_energy_replacing_fuel(self, 
                       original_inflows_dict,
                       original_outflows_dict,
                       recycled_qty,
                       recycle_io,
                       recyclate_flow,
                       toBeReplaced_flow,
                       max_replace_fraction=1.0,
                       combustion_eff = dat.combustion_efficiency_var,
                       scenario=dat.default_scenario,
                       emissions_list = dat.default_emissions,
                       write_to_console=False, 
                       **kwargs):
        """recycle_energy_replacing_fuel(original_inflows_dict, original_outflows_dict, recycled_qty, recycle_io, recyclate_flow, toBeReplaced_flow, max_replace_fraction=1.0, combustion_eff = dat.combustion_efficiency_var, scenario=dat.default_scenario, emissions_list = ['CO2', 'H2O', 'SO2'], **kwargs)
        replaces fuel use and associated emissions with a recycled energy flow (e.g. waste heat to replace combusted coal)

        Args:
            original_inflows_dict (defaultdict): Dictionary of inflow quantities from the orignal
                balancing of the unit process
            original_outflows_dict (defaultdict): Dictionary of outflow quantities from the orignal
                balancing of the unit process
            recycled_qty (float): quantity of recycled flow (energy)
            recycle_io (str): "i" if the recycled flow is an inflow or "o" if it is an outflow
            recyclate_flow (str): name of the recycled flow
            toBeReplaced_flow (str): name of the flow to be replaced by the recycled flow
            combustion_eff [str/float]: The name of the combustion efficiency variable (case sensitive) from the variables table
                or a float of the combustion_eff (must be between 0 and 1)
            scenario (str): name of the scenario to use
                (Defaults to dat.default_scenario)
            emissions_list (list[str]): list of emissions to recalculation. O2 is always automatically recalculated.
                (Defaults to ['CO2', 'H2O', 'SO2'])

        Returns:
            - *dictionary* of rebalanced inflows
            - *dictionary* of rebalanced outflows
            - *float* of the remaining quantity of the recycle stream

        """

        logger.info(f"{self.name.upper()}: Attempting to replace {toBeReplaced_flow} (energy) with {recyclate_flow}.")

        original_flows = dict(i=original_inflows_dict,
                              o=original_outflows_dict)
        rebalanced_flows = dict(i=copy(original_inflows_dict),
                                o=copy(original_outflows_dict))
        replaced_emissions_dict = defaultdict(float)
        replaced_inflows_dict = defaultdict(float)

        i_o =iof.clean_str(recycle_io[0])
        if i_o not in ['i', 'o']:
            raise KeyError(f'{self.name.upper()}: {i_o} is unknown flow location (Only inflows and outflows allowed for rebalanced processes')

        if toBeReplaced_flow in lookup_var_dict:
            toBeReplaced_flow = self.var_df.at[scenario, lookup_var_dict[toBeReplaced_flow]['lookup_var']] 

        if type(combustion_eff) is str:
            combustion_eff = self.var_df.at[scenario, combustion_eff]

        # calculate how much fuel energy will replace, including emissions/coinflows
        equivelent_fuel_qty = calc.Combustion(known_substance='energy', 
                                              qty=recycled_qty, 
                                              unknown_substance=toBeReplaced_flow, 
                                              var=combustion_eff, 
                                              emissions_list=emissions_list, 
                                              emissions_dict=replaced_emissions_dict, 
                                              inflows_dict=replaced_inflows_dict)

        logger.debug(f"{self.name.upper()}: {recycled_qty} of {recyclate_flow} assumed equivelent to {equivelent_fuel_qty} of {toBeReplaced_flow}")

        calc.check_qty(max_replace_fraction, fraction = True)

        replacable_qty = original_flows[i_o][toBeReplaced_flow] * max_replace_fraction
        unreplacable_qty = original_flows[i_o][toBeReplaced_flow] * (1 - max_replace_fraction)
        remaining_fuel_qty = replacable_qty - equivelent_fuel_qty

        if remaining_fuel_qty >= 0:
            rebalanced_flows[i_o][toBeReplaced_flow] = remaining_fuel_qty + unreplacable_qty
            rebalanced_flows[i_o][recyclate_flow] = recycled_qty
            remaining_energy_qty = 0

             # remove emissions/coinflows of replaced fuel
            for flow in replaced_emissions_dict:
                rebalanced_flows['o'][flow] -= replaced_emissions_dict[flow]

            for flow in replaced_inflows_dict:
                rebalanced_flows['i'][flow] -= replaced_inflows_dict[flow]

            remaining_energy_qty = 0

        else: #if remaining_fuel_qty is negative, that means there is a surplus of recycled energy
            rebalanced_flows[i_o][toBeReplaced_flow] = 0 + unreplacable_qty
            used_equivelent_fuel_qty = equivelent_fuel_qty + remaining_fuel_qty

            replaced_emissions_dict = defaultdict(float)
            replaced_inflows_dict = defaultdict(float)
            
            used_energy_qty = calc.Combustion(known_substance=toBeReplaced_flow, 
                                              qty=used_equivelent_fuel_qty, 
                                              unknown_substance='energy', 
                                              var=combustion_eff, 
                                              emissions_list=emissions_list, 
                                              emissions_dict=replaced_emissions_dict, 
                                              inflows_dict=replaced_inflows_dict)

            rebalanced_flows[i_o][recyclate_flow] += used_energy_qty
            remaining_energy_qty = recycled_qty - used_energy_qty
        
            # remove emissions/coinflows of replaced fuel
            for flow in replaced_emissions_dict:
                rebalanced_flows['o'][flow] -= replaced_emissions_dict[flow]
                if round(rebalanced_flows['o'][flow], dat.float_tol) == 0: # rounds off floating point errors
                    rebalanced_flows['o'][flow] = 0

            for flow in replaced_inflows_dict:
                rebalanced_flows['i'][flow] -= replaced_inflows_dict[flow]
                if round(rebalanced_flows['i'][flow], dat.float_tol) == 0: # rounds off floating point errors
                    rebalanced_flows['i'][flow] = 0

        if remaining_energy_qty < 0:
            raise ValueError(f"{self.name.upper()}: Something went wrong. remaining_recycle_qty < 0 {remaining_energy_qty}")

        if write_to_console is True:
            self.write_to_console(rebalanced_flows, scenario, str(used_equivelent_fuel_qty)+" (fuel eq)", recyclate_flow, toBeReplaced_flow)       
       
        return rebalanced_flows['i'], rebalanced_flows['o'], remaining_energy_qty


#####################
# SUBFUNCTIONS (used in unit.Balance())
        
    def check_io(self, i_o):
        """chekks that the flow location is valid
        """
        if type(i_o) is not str:
            if type(self.default_io) is not str:
                raise Exception('Flow location not specified')
            return self.default_io[0]
                
        i_o = iof.clean_str(i_o[0])
        if i_o not in ['i', 'o', 't']:
            raise Exception(f'{self.name.upper()}: {i_o} not valid product destination')
        return i_o

    
    def check_product(self, product):
        """checks that the product is valid
        """
        if product is False:
            return self.default_product
        if product is None:
            raise Exception('Please specify product to balance')
        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{self.name.upper()}: {product} not found in inflows or outflows')
        else:
            return product


    def make_io_dicts(self, product, qty, i_o, product_alt_name):
        """creates inflow and outflow dictionary and inserts starting product qty
        """
        io_dicts = {
            'i' : defaultdict(float),    # inflows dictionary
            'o' : defaultdict(float),    # outflows dictionary
            't' : defaultdict(float),    # temp dictionay (intermediate values - discarded)
            'e' : defaultdict(float),    # emissions dictionary (values added to outflows after all calculations)
            'c' : defaultdict(float),    # co-inflows dictionary (values added to inflows after all calculations)
        }

        # prime inflow or outflow dictionary with product quantity
        if product_alt_name is not False: 
            io_dicts[i_o][product_alt_name] = qty 
            logger.debug(f"{self.name.upper()}: {qty} of {product_alt_name} added to {i_o} dict, in place of {product}")
        else:
            io_dicts[i_o][product] = qty 
            logger.debug(f"{self.name.upper()}: {qty} of {product} added to {i_o} dict")

        return io_dicts


    def check_attempt(self, i, attempt, calc_df):
        """checks that the calculation attempt is valid
        """
        if attempt >= len(calc_df): 
            raise Exception(f"{self.name.upper()}: Cannot process {calc_df.iloc[i-1]}. Try checking flow location and remember that substance names are case sensitive.")
        if i >= len(calc_df):
            return 0   # if at end of list, loop around
        else:
            return i


    def check_var(self, var, calc_type, scenario):
        """checks that the variable is valid and returns the correct variable for the calc type
        """
        if isinstance(var, str) and iof.clean_str(var) not in dat.no_var:
            if calc_type in calc.lookup_var_calc_list:          # for lookup calculations the var specifies the column of the lookup df
                return iof.clean_str(var, lower=False)       # which is given as the var in the calc df
            else:                                               # otherwise looks up the variable in the var df
                return self.var_df.at[scenario, iof.clean_str(var)] # from the relevant scenario
        
        elif isinstance(var, (float, int, complex, np.integer, np.floating)):
            return var
        
        else:
            return None


    def check_substance(self, substance, scenario, product, product_alt_name, lookup_product_key):
        """checks that the substance name is valid and, if necesssary substitutes an alternative name 
        product_alt_name (str): from factory connection
        if in lookup_var_dict substitutes substance name from scenario in associated var_df column
            and identifies a lookup DF if needed
        if a unique_identifier suffix is used, returns a proxy of the generic substance name for
            use in calculations
        """
        lookup_df = False

        if product_alt_name is not False:
            if substance == product or substance == lookup_product_key:
                substance = product_alt_name #name at origin
                logger.debug(f"{self.name.upper()}: {product_alt_name} substitued for {product} as known substance")

        if substance in lookup_var_dict:
            if 'data_frame' in lookup_var_dict[substance]:
                logger.debug(f"{self.name.upper()}: {substance} has dataframe in lookup_var_dict")
                lookup_df = lookup_var_dict[substance]['data_frame']
            substance = self.var_df.at[scenario, lookup_var_dict[substance]['lookup_var']]
            logger.debug(f"{self.name.upper()}: lookup substance {substance} substituted")

        if dat.ignore_sep in substance:
            if substance.split(dat.ignore_sep)[0] in lookup_var_dict:
                logger.debug(f"{self.name.upper()}: {substance} in lookup_var_dict")
                if 'data_frame' in lookup_var_dict[substance.split(dat.ignore_sep)[0]]:
                    lookup_df = lookup_var_dict[substance.split(dat.ignore_sep)[0]]['data_frame']
                proxy = self.var_df.at[scenario, lookup_var_dict[substance.split(dat.ignore_sep)[0]]['lookup_var']]
                substance = proxy + dat.ignore_sep + substance.split(dat.ignore_sep)[1]
                logger.debug(f"{self.name.upper()}:lookup substance {substance} substituted")
            else:
                proxy = substance.split(dat.ignore_sep)[0]
            logger.debug(f"{self.name.upper()}: {dat.ignore_sep} separator found in {substance}. Using {proxy} for calculations.")
        else:
            proxy = substance

        return substance, proxy, lookup_df


    def check_lookup(self, known_lookup, unknown_lookup):
        """checks that only one lookup_df is available
        """
        if known_lookup is not False and unknown_lookup is not False:
            logger.debug(f"{self.name.upper()}: WARNING: Cannot use multiple lookup dictionaries. Using lookup dict specified for known substance")
            return known_lookup
        elif known_lookup is False:
            return unknown_lookup
        else:
            return known_lookup
       

    def check_calc(self, i, calc_type, calc_df, scenario, known_substance, known_io, unknown_substance, unknown_io, io_dicts):
        """checks whether inversion is needed, and whether all needed data is available
            if qty of the unknown substance but not known substance is available, inverts
            if neitehr qty is available, flags to skip to the next row
            if the calc requires two quantities, checks whether both qtys are available
                if not, flags to skip to the next row
        """
        skip = False
        known2_qty = None
        known2_proxy = None

        if calc_type not in calc.calcs_dict:
                raise Exception(f"{self.name.upper()}: {calc_type} is an unknown calculation type")

        if known_substance in io_dicts[known_io]:
            invert = False
        elif unknown_io not in io_dicts and unknown_io != 'd': #'d' can be used for discarded substances
            raise Exception(f"{self.name.upper()}: {unknown_io} is an unknown destination")
        elif unknown_io not in ['c', 'e'] and unknown_substance in io_dicts[unknown_io]:
            invert = True
        else: # when neither a qty of known or unknown substance is available
            return True, False, False, False

        if calc_type in calc.twoQty_calc_list: #e.g. addition or subtraction
            known2_substance = calc_df.at[i, dat.known2]
            k2_io = iof.clean_str(calc_df.at[i, dat.known2_io][0])

            if known2_substance in lookup_var_dict:
                known2_substance = self.var_df.at[scenario, lookup_var_dict[known2_substance]['lookup_var']] 

            if dat.ignore_sep in known2_substance:    
                if known2_substance.split(dat.ignore_sep)[0] in lookup_var_dict:
                    known2_proxy = self.var_df.at[scenario, lookup_var_dict[known2_substance.split(dat.ignore_sep)[0]]['lookup_var']]
                    known2_substance = known2_proxy + dat.ignore_sep + known2_substance.split(dat.ignore_sep)[1]
                else:
                    known2_proxy  = known2_substance.split(dat.ignore_sep)[0]  
                logger.debug(f"{self.name.upper()}: {dat.ignore_sep} separator found in {known2_substance}. Using {known2_proxy} for calculations.")          
            else:
                known2_proxy = known2_substance

            if known2_substance in io_dicts[k2_io]:
                known2_qty = io_dicts[k2_io][known2_substance]
            else: 
                logger.debug(f"{self.name.upper()}: {known2_substance} not found (both {known_substance} ({known_io}) and {known2_substance} ({k2_io}) required), skipping for now")
                return True, False, False, False

        return skip, invert, known2_qty, known2_proxy

        
    def write_to_console(self, io_dicts, scenario, qty, product, replacing=False):
        if type(replacing) is str:
            print(f"\n{str.upper(self.name)} rebalanced with {qty} of {product} replacing {replacing}.\n")
        
        else:
            print(f"\n{str.upper(self.name)} balanced on {qty} of {product} using {scenario} values.\n")

        flows = iof.mass_energy_df(dict(inflows=io_dicts['i'], outflows=io_dicts['o']))

        print(flows)
        print("\n")
