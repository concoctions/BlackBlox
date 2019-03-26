# -*- coding: utf-8 -*-
""" Unit process class

This module contains the Unit Process class, which is the smallest,
and fundamental, block used in BlackBlox.py.

Each unit process has inflows and outflows, whose abstract relationships 
are specified in a relationships table. The numeric values for the variables
used in those relationships are specified in a seperate table, to allow
for multipe scenarios to be used.

The Unit Process class has a single function, which is to balance the
inflows and outflows given one quantity of an inflow or outflow. Balancing
the unit process requires that the relationships table is complete.

Module Outline:

- import statements and logger
- module variable: df_units_library (dataframe)
- class: unit process
    - class function: Balance
    - class function: recycle_1to1
    - class function: recycle_energy_replacing_fuel

"""

from collections import defaultdict
from copy import copy
from math import isnan
from bb_log import get_logger
import io_functions as iof
import dataconfig as dat
import calculators  as calc

logger = get_logger("Unit Process")

# LOOK UP VARIABLES
df_unit_library = iof.make_df(dat.unit_process_library_file, 
                             sheet=dat.unit_process_library_sheet)
"""dataframe of all unit process names and file locations

This data frame is used by the unit process class to provide the
locations of the calculations and variable tables for each unit
process. Data locations for each unit process can also be provided
invidivually, but if not otherwise specified, the unit process
__init__ function will look for the data in this data frame.

The names of the unit process should be index column of the data
frame, and there should also be columns for the file paths of the
variables table and calculations tables. Columns for sheet names,
if the data is within excel sheets, will also be used if provided.

"""

lookup_var_dict = copy(dat.lookup_var_dict)
for var in lookup_var_dict:
    if 'filepath' in lookup_var_dict[var]:
        df = iof.make_df(lookup_var_dict[var]['filepath'], sheet=lookup_var_dict[var]['sheet'])
        lookup_var_dict[var]['data_frame'] = df


class UnitProcess:
    """UnitProcess(u_id, display_name=False, var_df=False, calc_df=False, units_df=df_unit_library)
    Unit processes have inflows and outflows with defined relationships.

    The relationships of the unit process flows must be defined so that

    Args:
        u_id (str): the unique ID of the process
        name (str/bool): a name 
        var_df (str/dataframe/bool): Optional. Dataframe or filepath tof
            tabular data of the variable values to use when balancing the 
            unit process. If False, __init__ uses df_unit_library to fetch 
            data.
            (Defaults to False)
        calc_df (str/dataframe/bool): Optional. Dataframe or filepath to 
            tabular data the relationships between the flows within the
            unit process, with each relationship having no more than a
            single variable. If False, __init__ uses df_unit_library to fetch
            data. The relationships must be sufficiently specified so that
            so that there are zero degrees of freedom. 
            (Defaults to False)
        units_df (dataframe): Unit process library data frame
            (Defaults to df_unit_library)

    Attributes:
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
        logger.debug(f"creating unit process object for {u_id}")

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

        #create sets of process inflows and outflows
        self.default_product = units_df.at[u_id, dat.unit_product]
        self.default_io = units_df.at[u_id, dat.unit_product_io]
        
        self.inflows = set() 
        self.outflows = set() 
        self.mass_inflows = set() 
        self.mass_outflows = set() 
        self.energy_inflows = set() 
        self.energy_outflows = set() 
        
        for i in self.calc_df.index: 
            # removes blank rows
            if type(self.calc_df.at[i, dat.known]) is str:
                products = [ (self.calc_df.at[i, dat.known], 
                    iof.clean_str(self.calc_df.at[i, dat.known_io][0])),
                        (self.calc_df.at[i, dat.unknown],
                        iof.clean_str(self.calc_df.at[i, dat.unknown_io][0]))]

            for product, i_o in products:
                if not product.startswith(dat.consumed_indicator): #ignores those that are said to be consumed
                    if i_o in ['i', 'c']:
                        self.inflows.add(product)
                        if iof.is_energy(product):
                            self.energy_inflows.add(product)
                        else:
                            self.mass_inflows.add(product)
                    elif i_o in ['o', 'e']:
                        self.outflows.add(product)
                        if iof.is_energy(product):
                            self.energy_outflows.add(product)
                        else:
                            self.mass_outflows.add(product)

                    if 'combustion' in self.calc_df.at[i, dat.calc_type]:
                        for emission in dat.default_emissions:
                            self.outflows.add(emission)
                            self.mass_outflows.add(emission)
                        self.energy_inflows.add(f"energy embodied in fuels")
                        self.energy_outflows.add("waste heat")
            
 
    def balance(self, 
                qty, 
                product=False, 
                i_o=False, 
                scenario=dat.default_scenario,
                product_alt_name=False,
                energy_flows=dat.energy_flows,
                balance_energy=True, 
                raise_imbalance=False,):
        """balance(self, qty, product=False, i_o=False, scenario=dat.default_scenario, energy_flows=dat.energy_flows, balance_energy=True, raise_imbalance=False,)
        performs a mass (and optionally energy) balance on the unit process.

        Calculates all inflows and outflows, using the specified variable values
        and relationship dataframe. Will only work if there are zero degrees of
        freedom in the specified relationships. Currently, only checks mass
        flows to see if they are properly balanced.

        Note:
            If the inflow mass and outflow mass are imbalanced an error will
            be raised and/or a "UNKNOWN MASS" or  "UNKNOWN ENERGY " flow will 
            be added to the offending flow dictionary with the imbalance quantity.

        Args:
            qty (float): The quantity of the specified flow.
            product (str/bool): the inflow or outflow on which to balance 
                the calculations. If False, uses the default product.
                (Defaults to False)
            i_o (str): 'i' or 'o', depending on whether the specified
                product is an inflow (i) or outflow (o). If False, uses the 
                default product's IO.
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

        if i_o is False:
            i_o = self.default_io
        i_o = iof.clean_str(i_o[0])
        if i_o not in ['i', 'o', 't']:
            raise Exception(f'{i_o} not valid product destination')
        
        if scenario not in self.var_df.index.values:
            raise Exception(f'{scenario} not found in variables file')
        
        if product is False:
            product = self.default_product
        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{product} not found in {self.name} inflows or outflows')
        if product in lookup_var_dict: # get product name from var_df, at variable specified in lookup_var_dict
            lookup_product_key = product 
            product = self.var_df.at[scenario, lookup_var_dict[product]['lookup_var']]  
        else:
            lookup_product_key = False

        calc_df = self.calc_df
        logger.debug(f"Attempting to balance {self.name} on {qty} of {product} (different name from origin: {product_alt_name}) ({i_o}) using {scenario} variables")

        io_dicts = {
            'i' : defaultdict(float),    # inflows dictionary
            'o' : defaultdict(float),    # outflows dictionary
            't' : defaultdict(float),    # temp dictionay (intermediate values - discarded)
            'e' : defaultdict(float),    # emissions dictionary (values added to outflows after all calculations)
            'c' : defaultdict(float),    # co-inflows dictionary (values added to inflows after all calculations)
        }

        # primes inflow or outflow dictionary with product quantity
        if product_alt_name is not False: 
            io_dicts[i_o][product_alt_name] = qty 
            logger.debug(f"{qty} of {product_alt_name} added to {i_o} dict, in place of {product}")
        else:
            io_dicts[i_o][product] = qty 
            logger.debug(f"{qty} of {product} added to {i_o} dict")

        i = 0
        attempt = 0

        while len(calc_df) > 0:     
            if i >= len(calc_df):
                i = 0   # if at end of list, loop around

            # removes blank rows; possibly doesn't work
            if type(calc_df.at[i, dat.known]) is not str or calc_df.at[i, dat.known] in dat.no_var:
                calc_df = calc_df.drop(i)
                calc_df = calc_df.reset_index(drop=True)
                attempt = 0
                logger.debug(f"known substance is not a string. Dropping this row")
                continue

            known_substance = calc_df.at[i, dat.known]
            known_io =iof.clean_str(calc_df.at[i, dat.known_io][0])
            unknown_io = iof.clean_str(calc_df.at[i, dat.unknown_io][0]) 
            unknown_substance = calc_df.at[i, dat.unknown]
            known_substance2 = None
            known_qty2 = None
            known2_proxy = None

            lookup_df = None

            calc_type = iof.clean_str(calc_df.at[i, dat.calc_type])
            invert = False

            var = None
            raw_var = calc_df.at[i, dat.calc_var]
            if isinstance(raw_var, str) and iof.clean_str(raw_var) not in dat.no_var:
                if calc_type in calc.lookup_var_calc_list:
                    var = iof.clean_str(raw_var, lower=False)
                else:
                    var = self.var_df.at[scenario, iof.clean_str(raw_var)]

            
            logger.debug(f"current index: {i}, current product: {known_substance}")
            if attempt >= len(calc_df): 
                print(io_dicts)
                raise Exception(f"Cannot process {known_substance} ({known_io}-flow), when trying to calculate {unknown_substance} ({unknown_io}-flow) via {calc_type}. Breaking to prevent infinite loop. Try checking flow location and remember that substance names are case sensitive.")
            
            # replaces product name with product_alt_name if and where applicable
            if product_alt_name is not False:
                if known_substance == product:
                    known_substance = product_alt_name #name at origin
                    logger.debug(f"{product_alt_name} substitued for {product} as known substance")
                elif lookup_product_key is not False:
                    if known_substance == lookup_product_key:
                        known_substance = product_alt_name #name at origin
                        logger.debug(f"{product_alt_name} substitued for {product} as known substance")
                if unknown_substance == product:
                    unknown_substance = product_alt_name #name at origin
                    logger.debug(f"{product_alt_name} substitued for {product} as unknown substance")
                elif lookup_product_key is not False:
                    if unknown_substance == lookup_product_key:
                        unknown_substance = product_alt_name #name at origin
                        logger.debug(f"{product_alt_name} substitued for {product} as unknown substance")

            # sets lookup_df for any lookup ratio calculations
            if known_substance in lookup_var_dict:
                if 'data_frame' in lookup_var_dict[known_substance]:
                    lookup_df = lookup_var_dict[known_substance]['data_frame']
                known_substance = self.var_df.at[scenario, lookup_var_dict[known_substance]['lookup_var']]
            if unknown_substance in lookup_var_dict:
                if lookup_df is not None and 'data frame' in lookup_var_dict[unknown_substance]:
                    print(f"[!] POSSIBLE ERROR [!] in ({self.name} unit process):\nBoth {known_substance} (known) and {unknown_substance} (unknown) are from lookup dicts. Only one lookup dict can be used for lookup-ratios. Defaulting to that of known substance.")
                else:
                    if 'data frame' in lookup_var_dict[unknown_substance]:
                        lookup_df = lookup_var_dict[unknown_substance]['data_frame']
                unknown_substance = self.var_df.at[scenario, lookup_var_dict[unknown_substance]['lookup_var']]

            #allows for the use of multiple flows that are the same substance by using an "ignore after" seperator
            if dat.ignore_sep in known_substance:
                if known_substance.split(dat.ignore_sep)[0] in lookup_var_dict:
                    lookup_df = lookup_var_dict[known_substance.split(dat.ignore_sep)[0]]['data_frame']
                    known_proxy = self.var_df.at[scenario, lookup_var_dict[known_substance.split(dat.ignore_sep)[0]]['lookup_var']]
                    known_substance = known_proxy + dat.ignore_sep + known_substance.split(dat.ignore_sep)[1]
                else:
                    known_proxy = known_substance.split(dat.ignore_sep)[0]
                logger.debug(f"{dat.ignore_sep} separator found in {known_substance}. Using {known_proxy} for calculations.")
            else:
                known_proxy = known_substance
            if dat.ignore_sep in unknown_substance:    
                if unknown_substance.split(dat.ignore_sep)[0] in lookup_var_dict:
                    lookup_df = lookup_var_dict[unknown_substance.split(dat.ignore_sep)[0]]['data_frame']                    
                    unknown_proxy = self.var_df.at[scenario, lookup_var_dict[unknown_substance.split(dat.ignore_sep)[0]]['lookup_var']]
                    unknown_substance = unknown_proxy + dat.ignore_sep + unknown_substance.split(dat.ignore_sep)[1]
                else:
                    unknown_proxy = unknown_substance.split(dat.ignore_sep)[0]  
                logger.debug(f"{dat.ignore_sep} separator found in {unknown_substance}. Using {unknown_proxy} for calculations.")          
            else:
                unknown_proxy = unknown_substance

            # checks if calculation inversion is necessary
            if known_substance in io_dicts[known_io]:
                pass
            elif unknown_io not in ['c', 'e'] and unknown_substance in io_dicts[unknown_io]:
                invert = True
                known_substance, unknown_substance = unknown_substance, known_substance
                known_io, unknown_io = unknown_io, known_io
                known_proxy, unknown_proxy = unknown_proxy, known_proxy
                logger.debug(f"{known_substance} not found, but {unknown_substance} found. Inverting calculations")
            else:
                i += 1
                attempt += 1
                logger.debug(f"neither {known_substance} nor {unknown_substance} found, skipping for now")
                continue
            
            if calc_type not in calc.calcs_dict:
                raise Exception(f"{calc_type} is an unknown calculation type")
            if unknown_io not in io_dicts and unknown_io != 'd': #'d' can be used for discarded substances
                raise Exception(f"{unknown_io} is an unknown destination")

            # if the calculation requires two known quantities, make sure both exist
            if calc_type in calc.twoQty_calc_list:
                known_substance2 = calc_df.at[i, dat.known2]
                k2_io = iof.clean_str(calc_df.at[i, dat.known2_io][0])

                if known_substance2 in lookup_var_dict:
                    known_substance2 = self.var_df.at[scenario, lookup_var_dict[known_substance2]['lookup_var']] 

                if dat.ignore_sep in known_substance2:    
                    if known_substance2.split(dat.ignore_sep)[0] in lookup_var_dict:
                        known2_proxy = self.var_df.at[scenario, lookup_var_dict[known_substance2.split(dat.ignore_sep)[0]]['lookup_var']]
                        known_substance2 = known2_proxy + dat.ignore_sep + known_substance2.split(dat.ignore_sep)[1]
                    else:
                        known2_proxy  = known_substance2.split(dat.ignore_sep)[0]  
                    logger.debug(f"{dat.ignore_sep} separator found in {known_substance2}. Using {known2_proxy} for calculations.")          
                else:
                    known2_proxy = known_substance2

                if known_substance2 in io_dicts[k2_io]:
                    known_qty2 = io_dicts[k2_io][known_substance2]
                else:
                    i += 1
                    attempt += 1
                    logger.debug(f"{known_substance2} not found (both {known_substance} ({known_io}) and {known_substance2} ({k2_io}) required), skipping for now")
                    continue

            qty_known = io_dicts[known_io][known_substance]
            
            kwargs = dict(qty=calc.no_nan(qty_known), 
                          var=calc.no_nan(var), 
                          known_substance=known_proxy, 
                          unknown_substance=unknown_proxy,
                          known_substance2 = known2_proxy,
                          qty2 = calc.no_nan(known_qty2),
                          invert=invert, 
                          emissions_dict=io_dicts['e'],
                          inflows_dict=io_dicts['c'],
                          lookup_df = lookup_df)
            kwargs = {**kwargs, **calc.calcs_dict[calc_type]['kwargs']}
            
            logger.debug(f"Attempting {calc_type} calculation for {unknown_substance} using {qty_known} of {known_substance}")
            qty_calculated = calc.calcs_dict[calc_type]['function'](**kwargs)
            qty_calculated = calc.no_nan(qty_calculated)

            if qty_calculated < 0:
                print(f"\n[!] POSSIBLE ERROR [!] in ({self.name} unit process): \nNegative number found:\n"
                      f"{qty_calculated} of {unknown_substance} calculated while performing {calc_type} using {qty_known} of {known_substance}")
                if known_substance2 is not None:
                    print(f"and {known_qty2} of {known_substance2}")
            
            if unknown_io in ['c', 'e']:
                io_dicts[unknown_io][unknown_substance] += qty_calculated
            elif unknown_io == 'd':
                pass
            else:
                io_dicts[unknown_io][unknown_substance] = qty_calculated

            calc_df = calc_df.drop(i)
            calc_df = calc_df.reset_index(drop=True)
            attempt = 0
            logger.debug(f"{qty_calculated} of {unknown_substance} calculated. {len(calc_df)} calculations remaining.")

        logger.debug(f"emissions: {io_dicts['e']}")
        logger.debug(f"coinflows: {io_dicts['c']}")
        for substance, qty in io_dicts['e'].items(): #adds emissions dictionary to outflow dictionary
            io_dicts['o'][substance] += qty
        for substance, qty in io_dicts['c'].items(): #adds co-inflows dictionary to inflows dictionary
            io_dicts['i'][substance] += qty

        total_mass_in, total_mass_out = calc.check_balance(io_dicts['i'], io_dicts['o'],
                                                 raise_imbalance=raise_imbalance, 
                                                 ignore_flows=energy_flows)

        if total_mass_in > total_mass_out:
            io_dicts['o']['UNKNOWN-mass'] = total_mass_in - total_mass_out
        elif total_mass_out > total_mass_in:
            io_dicts['i']['UNKNOWN-mass'] = total_mass_out - total_mass_in

        if balance_energy is True:
            logger.debug("Balancing energy")
            total_energy_in, total_energy_out = calc.check_balance(io_dicts['i'], io_dicts['o'],
                                                 raise_imbalance=raise_imbalance, 
                                                 ignore_flows=[],
                                                 only_these_flows=energy_flows)
            if total_energy_in > total_energy_out:
                io_dicts['o']['UNKNOWN-energy'] = total_energy_in - total_energy_out
            elif total_mass_out > total_mass_in:
                io_dicts['i']['UNKNOWN-energy'] = total_energy_out - total_energy_in

        logger.debug(f"{self.name} process balanced on {qty} of {product}")
        logger.debug('Inflows:')
        for substance, qty in io_dicts['i'].items():
            logger.debug(f"{substance}: {qty}")
        logger.debug('Outflows:')
        for substance, qty in io_dicts['o'].items():
            logger.debug(f"{substance}: {qty}")

        return io_dicts['i'], io_dicts['o']


    def recycle_1to1(self, 
                       original_inflows_dict,
                       original_outflows_dict,
                       recycled_qty,
                       recycle_io,
                       recycled_flow,
                       replaced_flow,
                       max_replace_fraction=1.0,
                       scenario=dat.default_scenario, 
                       **kwargs):
    
        """Inserts a recycle flow that corresponds 1-to-1 with an existing flow

        Args:
            original_inflows_dict (defaultdict): Dictionary of inflow quantities 
                from the orignal balancing of the unit process
            original_outflows_dict (defaultdict): Dictionary of outflow 
                quantities from the orignal balancing of the unit process
            recycled_qty (float): quantity of recycled flow
            recycle_io (str): "i" if the recycled flow is an inflow or "o" if 
                it is an outflow
            recycled_flow (str): name of the recycled flow
            replaced_flow (str): name of the flow to be replaced by the recycled flow
            max_replace_fraction (float/none): the maximum percentage of the 
                original flow that the recycled flow is allowed to replace

        Returns:
            - *dictionary* of rebalanced inflows
            - *dictionary* of rebalanced outflows
            - *float* of the remaining quantity of the recycle stream
        """

        original_flows = dict(i=original_inflows_dict,
                              o=original_outflows_dict)
        rebalanced_flows = dict(i=copy(original_inflows_dict),
                                o=copy(original_outflows_dict))
    

        i_o =iof.clean_str(recycle_io[0])

        if i_o not in ['i', 'o']:
            raise KeyError(f'{i_o} is unknown flow location (Only inflows and outflows allowed for rebalanced processes')

        if replaced_flow in lookup_var_dict:
            replaced_flow = self.var_df.at[scenario, lookup_var_dict[replaced_flow]['lookup_var']] 

        if replaced_flow in calc.df_fuels:
            logger.debug(f'WARNING! {replaced_flow} is a fuel. Combustion emissions will NOT be replaced. Use recycle_energy_replacing_fuel instead.')

        calc.check_qty(max_replace_fraction, fraction = True)
        replacable_qty = original_flows[i_o][replaced_flow] * max_replace_fraction
        unreplacable_qty = original_flows[i_o][replaced_flow] * (1 - max_replace_fraction)
        remaining_replacable_qty = replacable_qty - recycled_qty

        if remaining_replacable_qty >= 0:
            rebalanced_flows[i_o][replaced_flow] = remaining_replacable_qty + unreplacable_qty
            rebalanced_flows[i_o][recycled_flow] += recycled_qty
            remaining_recycle_qty = 0

        else:
            rebalanced_flows[i_o][replaced_flow] = 0 + unreplacable_qty
            used_recycle_qty = recycled_qty + remaining_replacable_qty
            rebalanced_flows[i_o][recycled_flow] += used_recycle_qty
            remaining_recycle_qty = recycled_qty - used_recycle_qty

        if remaining_recycle_qty < 0:
            raise ValueError(f"Something went wrong. remaining_recycle_qty < 0 {remaining_recycle_qty}")

        return rebalanced_flows['i'], rebalanced_flows['o'], remaining_recycle_qty


    def recycle_energy_replacing_fuel(self, 
                       original_inflows_dict,
                       original_outflows_dict,
                       recycled_qty,
                       recycle_io,
                       recycled_flow,
                       replaced_flow,
                       max_replace_fraction=1.0,
                       combustion_eff = dat.combustion_efficiency_var,
                       scenario=dat.default_scenario,
                       emissions_list = dat.default_emissions, 
                       **kwargs):
        """recycle_energy_replacing_fuel(original_inflows_dict, original_outflows_dict, recycled_qty, recycle_io, recycled_flow, replaced_flow, max_replace_fraction=1.0, combustion_eff = dat.combustion_efficiency_var, scenario=dat.default_scenario, emissions_list = ['CO2', 'H2O', 'SO2'], **kwargs)
        replaces fuel use and associated emissions with a recycled energy flow

        Args:
            original_inflows_dict (defaultdict): Dictionary of inflow quantities from the orignal
                balancing of the unit process
            original_outflows_dict (defaultdict): Dictionary of outflow quantities from the orignal
                balancing of the unit process
            recycled_qty (float): quantity of recycled flow
            recycle_io (str): "i" if the recycled flow is an inflow or "o" if it is an outflow
            recycled_flow (str): name of the recycled flow
            replaced_flow (str): name of the flow to be replaced by the recycled flow
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

        logger.debug(f"Attempting to replace {replaced_flow} (energy) with {recycled_flow}.")

        original_flows = dict(i=original_inflows_dict,
                              o=original_outflows_dict)
        rebalanced_flows = dict(i=copy(original_inflows_dict),
                                o=copy(original_outflows_dict))

        i_o =iof.clean_str(recycle_io[0])

        if i_o not in ['i', 'o']:
            raise KeyError(f'{i_o} is unknown flow location (Only inflows and outflows allowed for rebalanced processes')

        if replaced_flow in lookup_var_dict:
            replaced_flow = self.var_df.at[scenario, lookup_var_dict[replaced_flow]['lookup_var']] 

        if type(combustion_eff) is str:
            combustion_eff = self.var_df.at[scenario, combustion_eff]

        replaced_emissions_dict = defaultdict(float)
        replaced_inflows_dict = defaultdict(float)
        equivelent_fuel_qty = calc.Combustion('energy', 
                                          recycled_qty, 
                                          replaced_flow, 
                                          combustion_eff, 
                                          replaced_emissions_dict,
                                          replaced_inflows_dict,
                                          emissions_list=emissions_list)

        calc.check_qty(max_replace_fraction, fraction = True)

        replacable_qty = original_flows[i_o][replaced_flow] * max_replace_fraction
        unreplacable_qty = original_flows[i_o][replaced_flow] * (1 - max_replace_fraction)
        remaining_fuel_qty = replacable_qty - equivelent_fuel_qty

        if remaining_fuel_qty >= 0:
            rebalanced_flows[i_o][replaced_flow] = remaining_fuel_qty + unreplacable_qty
            rebalanced_flows[i_o][recycled_flow] = recycled_qty
            remaining_energy_qty = 0

            for flow in replaced_emissions_dict:
                rebalanced_flows['o'][flow] -= replaced_emissions_dict[flow]

            for flow in replaced_inflows_dict:
                rebalanced_flows['i'][flow] -= replaced_inflows_dict[flow]

            remaining_energy_qty = 0

        else: #if remaining_fuel_qty is negative, that means there is unused recycled energy
            rebalanced_flows[i_o][replaced_flow] = 0 + unreplacable_qty
            used_equivelent_fuel_qty = equivelent_fuel_qty + remaining_fuel_qty

            replaced_emissions_dict = defaultdict(float)
            replaced_inflows_dict = defaultdict(float)
            
            used_energy_qty = calc.Combustion(replaced_flow, 
                                         used_equivelent_fuel_qty, 
                                         'energy', 
                                         combustion_eff, 
                                         replaced_emissions_dict,
                                         replaced_inflows_dict,
                                         emissions_list=emissions_list)

            rebalanced_flows[i_o][recycled_flow] += used_energy_qty
            remaining_energy_qty = recycled_qty - used_energy_qty
        
            for flow in replaced_emissions_dict:
                rebalanced_flows['o'][flow] -= replaced_emissions_dict[flow]
                if round(rebalanced_flows['o'][flow], 8) == 0: # rounds off floating point errors
                    rebalanced_flows['o'][flow] = 0
            for flow in replaced_inflows_dict:
                rebalanced_flows['i'][flow] -= replaced_inflows_dict[flow]
                if round(rebalanced_flows['i'][flow], 8) == 0: # rounds off floating point errors
                    rebalanced_flows['i'][flow] = 0

        if remaining_energy_qty < 0:
            raise ValueError(f"Something went wrong. remaining_recycle_qty < 0 {remaining_energy_qty}")

        return rebalanced_flows['i'], rebalanced_flows['o'], remaining_energy_qty
    
        


