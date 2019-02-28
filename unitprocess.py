# -*- coding: utf-8 -*-
""" Unit process class

This module contains the Unit Process class, which is the smallest,
and fundamental, block used in BlackBlox.py.

Each unit process has inflows and outflows, whose abstract relationships 
are specified in a relationships table. The numeric values for the variables
used in those relationships are specified in a seperate table, to allow
for multipe scenarios to be 

The Unit Process class has a single function, which is to balance the
inflows and outflows given one quantity of an inflow or outflow. Balancing
the unit process requires that the relationships table is complete.

Module Outline:

- import statements and logger
- module variable: df_units_library (dataframe)
- class: unit process
    - class function: Balance

"""

from collections import defaultdict
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

lookup_var_dict = { 
    'fuel': dict(data_frame=calc.df_fuels, 
                 lookup_var='fuelType'),
    'fossil fuel': dict(data_frame=calc.df_fuels, 
                 lookup_var='fossil fuel type'),
    'biofuel': dict(data_frame=calc.df_fuels, 
                 lookup_var='biofuel type')
    } 
"""dictionary of special lookup substance names
Lookup_var_dict is a dictionary with the names of substance, that when used
in the unit process calculations file, will trigger the program to replace
the lookup substance name with the substance name specified in the unit 
process's variable data table for the scenario currently in use.

Each entry in this dictionary should be formatted as follows:
    key (str): the substance name to be used in the calcuations file
    value (dict): a dictionary of lookup variable attributes.
        lookup_var (str): the header of the column in the unit process 
            variable file that contains the value with which to replace
            the lookup substance word.
        data_frame (optional): a data frame with additional custom data
            about the lookup variable, such as to be used in custom functions,
            below. These are not used elsewhere in BlackBlox.py.
"""

class UnitProcess:
    """Unit processes have inflows and outflows with defined relationships.

    The relationships of the unit process flows must be defined so that

    Args:
        name (str): Unique name for the process
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
        name (str): Name of process
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
                 name, 
                 var_df=False, 
                 calc_df=False, 
                 units_df=df_unit_library):
        logger.debug(f"creating unit process object for {name}")
        self.name = name

        if var_df is not False:
            self.var_df = iof.make_df(var_df)
        else:
            v_sheet = iof.check_for_col(units_df, dat.var_sheetname, name)
            self.var_df = iof.make_df(units_df.at[name, dat.var_filepath], 
                                      sheet=v_sheet)

        if calc_df is not False:
            self.calc_df = calc_df
        else:
            c_sheet = iof.check_for_col(units_df, dat.calc_sheetname, name)
            self.calc_df = iof.make_df(units_df.at[name, dat.calc_filepath], 
                                       sheet=c_sheet, 
                                       index=None)

        #create sets of process inflows and outflows
        self.default_product = units_df.at[name, dat.unit_product]
        self.default_io = units_df.at[name, dat.unit_product_io]
        
        self.inflows = set() 
        self.outflows = set() 
        
        for i in self.calc_df.index: 
            products = [ (self.calc_df.at[i, dat.known], 
                iof.clean_str(self.calc_df.at[i, dat.known_io][0])),
                 (self.calc_df.at[i, dat.unknown],
                 iof.clean_str(self.calc_df.at[i, dat.unknown_io][0]))]

            for product, i_o in products:
                if i_o == 'i':
                    self.inflows.add(product)
                elif i_o == 'o':
                    self.outflows.add(product)
            
 
    def balance(self, 
                qty, 
                product=False, 
                i_o=False, 
                var_i=dat.default_scenario,
                energy_flows=dat.energy_flows,
                balance_energy=True, 
                raise_imbalance=False,):
        """performs a mass (and optionally energy) balance on the unit process.

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
            var_i (str): row index of var_df to use for the variables value,
                generally corresponding to the name of the scenario. If
                False, uses the default scenario index specified in 
                dataconfig.
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
            Defaultdict of inflows with substance names as keys and quantities
                as values
            Defaultdict of outflows with substance names as keys and quantities
                as values.
        """

        if i_o is False:
            i_o = self.default_io
        i_o = iof.clean_str(i_o[0])
        if i_o not in ['i', 'o', 't']:
            raise Exception(f'{i_o} not valid product destination')
        if var_i not in self.var_df.index.values:
            raise Exception(f'{var_i} not found in variables file')
        if product is False:
            product = self.default_product
        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{product} not found in {self.name} inflows or outflows')
        if product in lookup_var_dict:
            product = self.var_df.at[var_i, lookup_var_dict[product]['lookup_var']]   
        calc_df = self.calc_df
        logger.debug(f"Attempting to balance {self.name} on {qty} of {product} ({i_o}) using {var_i} variables")

        io_dicts = {
            'i' : defaultdict(float),    # inflows dictionary
            'o' : defaultdict(float),    # outflows dictionary
            't' : defaultdict(float),    # temp dictionay (intermediate values - discarded)
            'e' : defaultdict(float),    # emissions dictionary (values added to outflows after all calculations)
            'c' : defaultdict(float),    # co-inflows dictionary (values added to inflows after all calculations)
        }
        io_dicts[i_o][product] = qty # primes inflow or outflow dictionary with product quantity
        i = 0
        attempt = 0

        while len(calc_df) > 0:     
            if i >= len(calc_df):
                i = 0   # if at end of list, loop around

            known_substance = calc_df.at[i, dat.known]
            known_io =iof.clean_str(calc_df.at[i, dat.known_io][0])
            unknown_io = iof.clean_str(calc_df.at[i, dat.unknown_io][0]) 
            unknown_substance = calc_df.at[i, dat.unknown]
            calc_type = iof.clean_str(calc_df.at[i, dat.calc_type])
            invert = False
            var = None
            known_substance2 = None
            known_qty2 = None
            if iof.clean_str(calc_df.at[i, dat.calc_var]) not in dat.no_var:
                var = self.var_df.at[var_i, calc_df.at[i, dat.calc_var]] 

            logger.debug(f"current index: {i}, current product: {known_substance}")
            if attempt >= len(calc_df): 
                raise Exception(f"Cannot process {known_substance}. Breaking to prevent infinite loop")

            if known_substance in lookup_var_dict:
                known_substance = self.var_df.at[var_i, lookup_var_dict[known_substance]['lookup_var']] 
            if unknown_substance in lookup_var_dict:
                unknown_substance = self.var_df.at[var_i, lookup_var_dict[unknown_substance]['lookup_var']] 

            if known_substance in io_dicts[known_io]:
                pass
            elif unknown_io not in ['c', 'e'] and unknown_substance in io_dicts[unknown_io]:
                invert = True
                known_substance, unknown_substance = (unknown_substance, known_substance)
                known_io, unknown_io = unknown_io, known_io
                logger.debug(f"{known_substance} not found, but {unknown_substance} found. Inverting calculations")
            else:
                i += 1
                attempt += 1
                logger.debug(f"neither {known_substance} nor {unknown_substance} found, skipping for now")
                continue
            
            if calc_type not in calc.calcs_dict:
                raise Exception(f"{calc_type} is an unknown_substance calculation type")
            if unknown_io not in io_dicts:
                raise Exception(f"{unknown_io} is an unknown destination")

            if calc_type in calc.twoQty_calc_list:
                known_substance2 = calc_df.at[i, dat.known2]
                k2_io = iof.clean_str(calc_df.at[i, dat.known2_io][0])
                if known_substance2 in lookup_var_dict:
                    known_substance2 = self.var_df.at[var_i, lookup_var_dict[known_substance]['lookup_var']] 
                if known_substance2 in io_dicts[k2_io]:
                    known_qty2 = io_dicts[k2_io][known_substance2]
                else:
                    attempt += 1
                    logger.debug(f"{known_substance2} not found (both {known_substance} ({known_io}) and {known_substance2} ({k2_io}) required), skipping for now")
                    continue

            qty_known = io_dicts[known_io][known_substance]
            kwargs = dict(qty=qty_known, 
                          var=var, 
                          known_substance=known_substance, 
                          unknown_substance=unknown_substance,
                          known_substance2 =  known_substance2,
                          qty2 = known_qty2,
                          invert=invert, 
                          emissions_dict=io_dicts['e'],
                          inflows_dict=io_dicts['c'])
            logger.debug(f"Attempting {calc_type} calculation for {unknown_substance} using {qty_known} of {known_substance}")
            qty_calculated = calc.calcs_dict[calc_type](**kwargs)
            io_dicts[unknown_io][unknown_substance] = qty_calculated

            calc_df = calc_df.drop(i)
            calc_df = calc_df.reset_index(drop=True)
            attempt = 0
            logger.debug(f"{qty_calculated} of {unknown_substance} calculated. {len(calc_df)} calculations remaining.")

        for substance, qty in io_dicts['e'].items(): #adds emissions dictionary to outflow dictionary
            io_dicts['o'][substance] += qty
        for substance, qty in io_dicts['c'].items(): #adds co-inflows dictionary to inflows dictionary
            io_dicts['i'][substance] += qty

        logger.debug(f"{self.name} process balanced on {qty} of {product}")
        logger.debug('Inflows:')
        for substance, qty in io_dicts['i'].items():
            logger.debug(f"{substance}: {qty}")
        logger.debug('Outflows:')
        for substance, qty in io_dicts['o'].items():
            logger.debug(f"{substance}: {qty}")

        total_mass_in, total_mass_out = calc.check_balance(io_dicts['i'], io_dicts['o'],
                                                 raise_imbalance=raise_imbalance, 
                                                 ignore_flows=energy_flows)

        if total_mass_in > total_mass_out:
            io_dicts['i']['UNKNOWN_MASS'] = total_mass_in - total_mass_out
        elif total_mass_out > total_mass_in:
            io_dicts['o']['UNKNOWN_MASS'] = total_mass_out - total_mass_in

        if balance_energy is True:
            total_energy_in, total_energy_out = calc.check_balance(io_dicts['i'], io_dicts['o'],
                                                 raise_imbalance=raise_imbalance, 
                                                 only_these_flows=energy_flows)

        if total_energy_in > total_energy_out:
            io_dicts['i']['UNKNOWN_ENERGY'] = total_energy_in - total_energy_out
        elif total_mass_out > total_mass_in:
            io_dicts['o']['UNKNOWN_ENERGY'] = total_energy_out - total_energy_in

        return io_dicts['i'], io_dicts['o']


    def recycle_1to1(self, 
                       original_inflows_dict,
                       original_outflows_dict,
                       recycled_qty,
                       recycle_io,
                       recycled_flow,
                       replaced_flow,
                       var_i=dat.default_scenario):
    
        """Inserts a recycle flow that corresponds 1-to-1 with an existing flow

        Args:
            recycled_qty (float): quantity of recycled flow
        """

        original_flows = dict(i=original_inflows_dict,
                              o=original_outflows_dict)
        rebalanced_flows = original_flows.copy()

        i_o =iof.clean_str(recycled_io[0])

        if i_o not in ['i', 'o']:
            raise KeyError(f'{recycled_io} is unknown flow location (Only inflows and outflows allowed for rebalanced processes')

        if replaced_flow in lookup_var_dict:
            replaced_flow = self.var_df.at[var_i, lookup_var_dict[replaced_flow]['lookup_var']] 

        if replaced_flow in df_fuels:
            print(f'WARNING! {replaced_flow} is a fuel. Combustion emissions will NOT be replaced. Use recycle_energy_replacing_fuel instead.')

        remaining_replaced_qty = original_flows[i_o][replaced_flow] - recycled_qty

        if remaining_replaced_qty >= 0:
            rebalanced_flows[i_o][replaced_flow] = remaining_replaced_qty
            rebalanced_flows[i_o][recycled_flow] += recycled_qty
            remaining_recycle_qty = 0

        else:
            rebalanced_flows[i_o][replaced_flow] = 0
            used_recycle_qty = recycled_qty + remaining_replaced_qty
            rebalanced_flow[i_o][recycled_flow] += used_recycle_qty
            remaining_recycle_qty = recycled_qty - used_recycle_qty

        if remaining_recylce_qty < 0:
            raise ValueError(f"Something went wrong. remaining_recycle_qty < 0 {remaining_recycle_qty}")

        return rebalanced_inflows_dict, rebalanced_outflows_dict, remaining_recycle_qty


    def recycle_energy_replacing_fuel(self, 
                       original_inflows_dict,
                       original_outflows_dict,
                       recycled_energy_qty,
                       recycle_io,
                       recycled_energy,
                       replaced_fuel,
                       var_i=dat.default_scenario,
                       combustion_efficiency,
                       emissions_list = ['CO2', 'H2O', 'SO2']):
        """replaces fuel use and associated emissions with a recycled energy flow
        """

        
        original_flows = dict(i=original_inflows_dict,
                              o=original_outflows_dict)
        rebalanced_flows = original_flows.copy()

        i_o =iof.clean_str(recycled_io[0])

        if i_o not in ['i', 'o']:
            raise KeyError(f'{recycled_io} is unknown flow location (Only inflows and outflows allowed for rebalanced processes')

        if replaced_fuel in lookup_var_dict:
            replaced_fuel = self.var_df.at[var_i, lookup_var_dict[replaced_fuel]['lookup_var']] 

        if type(combustion_efficiency) is str:
            combustion_efficiency = self.var_df.at[var_i, iof.clean_str(combution_efficiency)]

        replaced_emissions_dict = defaultdict(float)
        replaced_inflows_dict = ddefaultdict(float)
        equivelent_fuel_qty = Combustion('energy', 
                                          recycled_energy_qty, 
                                          replaced_fuel, 
                                          combustion_efficiency, 
                                          replaced_emissions_dict,
                                          replaced_inflows_dict,
                                          emissions_list=emissions_list)

        remaining_fuel = original_flows[i_o][replaced_fuel] - equivelent_fuel_qty

        if remaining_fuel >= 0:
            rebalanced_flows[i_o][replaced_fuel] = remaining_replaced_qty
            rebalanced_flows[i_o][recycled_energy] = recycled_qty
            remaining_recycle_qty = 0

            for flow in emissions_dict:
                rebalanced_flows['o'][flow] -= replaced_emissions_dict[flow]

            for flow in inflows_dict:
                rebalanced_flows['i'][flow] -= replaced_inflows_dict[flow]

            remaining_energy_qty = 0

        else:
            rebalanced_flows[i_o][replaced_flow] = 0
            used_equivelent_fuel_qty = equivelent_fuel_qty + remaining_fuel

            replaced_emissions_dict = defaultdict(float)
            replaced_inflows_dict = ddefaultdict(float)
            used_energy_qty = Combustion(replaced_fuel, 
                                         used_equivelent_fuel_qty, 
                                         'energy', 
                                         combustion_efficiency, 
                                         replaced_emissions_dict,
                                         replaced_inflows_dict,
                                         emissions_list=emissions_list)

            rebalanced_flows[i_o][recycled_energy] += used_energy_qty
            remaining_energy_qty = recycled_energy_qty - used_energy_qty
        
            for flow in emissions_dict:
                rebalanced_flows['o'][flow] -= replaced_emissions_dict[flow]
            for flow in inflows_dict:
                rebalanced_flows['i'][flow] -= replaced_inflows_dict[flow]

        if remaining_recycle_qty < 0:
            raise ValueError(f"Something went wrong. remaining_recycle_qty < 0 {remaining_recycle_qty}")

        return rebalanced_inflows_dict, rebalanced_outflows_dict, remaining_energy_qty
    
        


