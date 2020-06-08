# -*- coding: utf-8 -*-
""" Unit process class

This module contains the Unit Process class, which fundamenta building block of
blackblox.py



The primary function of the unit process class, Balance, calculates all the 
inflows and outflows of the unit proces based on a single specified flow quantity.

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

This data frame provides the locations of the calculations and variable tables 
for one or more unit process. Data locations for each unit process can also be 
provided invidivually when creating the a specific instance of a unit process 
class.

The index of the table contains the unique idenitifer of the unit processes
and the columns contains the location of the variable and calculation tables.
"""

lookup_var_dict = copy(dat.lookup_var_dict)
for var in lookup_var_dict:
    if 'filepath' in lookup_var_dict[var]:
        df = iof.make_df(lookup_var_dict[var]['filepath'], sheet=lookup_var_dict[var]['sheet'])
        lookup_var_dict[var]['data_frame'] = df


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

        #identify process inflows and outflows
        if dat.unit_product in units_df:
            self.default_product = units_df.at[u_id, dat.unit_product]
        else:
            self.default_product = None

        if dat.unit_product_io in units_df:
            self.default_io = units_df.at[u_id, dat.unit_product_io]
        else:
            self.default_io = None
        
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
                qty, 
                product=False, 
                i_o=False, 
                scenario=dat.default_scenario,
                product_alt_name=False,
                energy_flows=dat.energy_flows,
                balance_energy=True, 
                raise_imbalance=False,):

        i_o = check_io(i_o, self.default_io)

    
        return io_dicts['i'], io_dicts['o']


#####################
# SUBFUNCTIONS
        
def check_io(i_o, default_io):
    if type(i_o) is not str:
        if type(default_io) is not str:
            raise Exception('Flow location not specified')
        return default_io
            
    i_o = iof.clean_str(i_o[0])
    if i_o not in ['i', 'o', 't']:
        raise Exception(f'{self.name.upper()}: {i_o} not valid product destination')
    return i_o



############
# ORIGINAL PIECES
                
        if product is False:
            product = self.default_product
            if product is None:
                raise Exception('Please specify product to balance')
        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{self.name.upper()}: {product} not found in inflows or outflows')
        if product in lookup_var_dict: # get product name from var_df, at variable specified in lookup_var_dict
            lookup_product_key = product 
            product = self.var_df.at[scenario, lookup_var_dict[product]['lookup_var']]  
        else:
            lookup_product_key = False

        if scenario not in self.var_df.index.values:
            raise Exception(f'{self.name.upper()}: {scenario} not found in variables file')

        calc_df = self.calc_df
        logger.debug(f"{self.name.upper()}: Attempting to balance on {qty} of {product} (different name from origin: {product_alt_name}) ({i_o}) using {scenario} variables")

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
            logger.debug(f"{self.name.upper()}: {qty} of {product_alt_name} added to {i_o} dict, in place of {product}")
        else:
            io_dicts[i_o][product] = qty 
            logger.debug(f"{self.name.upper()}: {qty} of {product} added to {i_o} dict")

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
                logger.debug(f"{self.name.upper()}: known substance is not a string. Dropping this row")
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
                if calc_type in calc.lookup_var_calc_list:          # for lookup calculations the var specifies the column of the lookup df
                    var = iof.clean_str(raw_var, lower=False)       # which is given as the var in the calc df
                else:                                               # otherwise looks up the variable in the var df
                    var = self.var_df.at[scenario, iof.clean_str(raw_var)] # from the relevant scenario

            
            logger.debug(f"{self.name.upper()}: current index: {i}, current product: {known_substance}")
            if attempt >= len(calc_df): 
                print(io_dicts)
                raise Exception(f"{self.name.upper()}: Cannot process {known_substance} ({known_io}-flow), when trying to calculate {unknown_substance} ({unknown_io}-flow) via {calc_type}. Breaking to prevent infinite loop. Try checking flow location and remember that substance names are case sensitive.")
            
            # replaces product name with product_alt_name if and where applicable
            if product_alt_name is not False:
                if known_substance == product:
                    known_substance = product_alt_name #name at origin
                    logger.debug(f"{self.name.upper()}: {product_alt_name} substitued for {product} as known substance")
                elif lookup_product_key is not False:
                    if known_substance == lookup_product_key:
                        known_substance = product_alt_name #name at origin
                        logger.debug(f"{self.name.upper()}: {product_alt_name} substitued for {product} as known substance")
                if unknown_substance == product:
                    unknown_substance = product_alt_name #name at origin
                    logger.debug(f"{self.name.upper()}: {product_alt_name} substitued for {product} as unknown substance")
                elif lookup_product_key is not False:
                    if unknown_substance == lookup_product_key:
                        unknown_substance = product_alt_name #name at origin
                        logger.debug(f"{self.name.upper()}: {product_alt_name} substitued for {product} as unknown substance")

            # sets lookup_df for any lookup ratio calculations
            if known_substance in lookup_var_dict:
                if 'data_frame' in lookup_var_dict[known_substance]:
                    lookup_df = lookup_var_dict[known_substance]['data_frame']
                known_substance = self.var_df.at[scenario, lookup_var_dict[known_substance]['lookup_var']]
            if unknown_substance in lookup_var_dict:
                if lookup_df is not None and 'data_frame' in lookup_var_dict[unknown_substance]:
                    print(f"[!] POSSIBLE ERROR [!] in ({self.name} unit process):\nBoth {known_substance} (known) and {unknown_substance} (unknown) are from lookup dicts. Only one lookup dict can be used for lookup-ratios. Defaulting to that of known substance.")
                else:
                    if 'data_frame' in lookup_var_dict[unknown_substance]:
                        lookup_df = lookup_var_dict[unknown_substance]['data_frame']
                unknown_substance = self.var_df.at[scenario, lookup_var_dict[unknown_substance]['lookup_var']]

            #ignores unique-identifier suffixes to allows for multiple flows of the same substance
            logger.debug("if you get an error here, check in the var file that you don't have a number where you should have a string") #I don't remember exactly how this applies
            if dat.ignore_sep in known_substance:
                if known_substance.split(dat.ignore_sep)[0] in lookup_var_dict:
                    lookup_df = lookup_var_dict[known_substance.split(dat.ignore_sep)[0]]['data_frame']
                    known_proxy = self.var_df.at[scenario, lookup_var_dict[known_substance.split(dat.ignore_sep)[0]]['lookup_var']]
                    known_substance = known_proxy + dat.ignore_sep + known_substance.split(dat.ignore_sep)[1]
                else:
                    known_proxy = known_substance.split(dat.ignore_sep)[0]
                logger.debug(f"{self.name.upper()}: {dat.ignore_sep} separator found in {known_substance}. Using {known_proxy} for calculations.")
            else:
                known_proxy = known_substance
            if dat.ignore_sep in unknown_substance:    
                if unknown_substance.split(dat.ignore_sep)[0] in lookup_var_dict:
                    lookup_df = lookup_var_dict[unknown_substance.split(dat.ignore_sep)[0]]['data_frame']                    
                    unknown_proxy = self.var_df.at[scenario, lookup_var_dict[unknown_substance.split(dat.ignore_sep)[0]]['lookup_var']]
                    unknown_substance = unknown_proxy + dat.ignore_sep + unknown_substance.split(dat.ignore_sep)[1]
                else:
                    unknown_proxy = unknown_substance.split(dat.ignore_sep)[0]  
                logger.debug(f"{self.name.upper()}: {dat.ignore_sep} separator found in {unknown_substance}. Using {unknown_proxy} for calculations.")          
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
                logger.debug(f"{self.name.upper()}: {known_substance} not found, but {unknown_substance} found. Inverting calculations")
            else:
                i += 1
                attempt += 1
                logger.debug(f"{self.name.upper()}: neither {known_substance} nor {unknown_substance} found, skipping for now")
                continue
            
            if calc_type not in calc.calcs_dict:
                raise Exception(f"{self.name.upper()}: {calc_type} is an unknown calculation type")
            if unknown_io not in io_dicts and unknown_io != 'd': #'d' can be used for discarded substances
                raise Exception(f"{self.name.upper()}: {unknown_io} is an unknown destination")

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
                    logger.debug(f"{self.name.upper()}: {dat.ignore_sep} separator found in {known_substance2}. Using {known2_proxy} for calculations.")          
                else:
                    known2_proxy = known_substance2

                if known_substance2 in io_dicts[k2_io]:
                    known_qty2 = io_dicts[k2_io][known_substance2]
                else:
                    i += 1
                    attempt += 1
                    logger.debug(f"{self.name.upper()}: {known_substance2} not found (both {known_substance} ({known_io}) and {known_substance2} ({k2_io}) required), skipping for now")
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
            
            logger.debug(f"{self.name.upper()}: Attempting {calc_type} calculation for {unknown_substance} using {qty_known} of {known_substance}")
            qty_calculated = calc.calcs_dict[calc_type]['function'](**kwargs)
            qty_calculated = calc.no_nan(qty_calculated)

            if qty_calculated < 0:
                print(f"{self.name.upper()}:\n[!] POSSIBLE ERROR [!]\nNegative number found:\n"
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
            logger.debug(f"{self.name.upper()}: {qty_calculated} of {unknown_substance} calculated. {len(calc_df)} calculations remaining.")

        logger.debug(f"{self.name.upper()}: emissions: {io_dicts['e']}")
        logger.debug(f"{self.name.upper()}: coinflows: {io_dicts['c']}")
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
            logger.debug("{self.name.upper()}: Balancing energy")
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
