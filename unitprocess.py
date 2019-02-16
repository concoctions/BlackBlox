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
import custom_lookup as lup


logger = get_logger("Unit Process")


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

    def __init__(self, name, var_df=False, calc_df=False, 
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
            
 
    def balance(self, qty, product=False, i_o=False, 
                var_i=False):
        """performs a mass balance on the unit process.

        Except doesn't actually "balance" at the moment; just calculates
        flow quantities as specified in the relationships table.

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
        if var_i is False:
            var_i = dat.default_scenario
        if var_i not in self.var_df.index.values:
            raise Exception(f'{var_i} not found in variables file')
        if product is False:
            product = self.default_product
        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{product} not found in {self.name} inflows or outflows')
        if product in lup.lookup_var_dict:
            product = self.var_df.at[var_i, lup.lookup_var_dict[product]['lookup_var']]   
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
            var = False
            if iof.clean_str(calc_df.at[i, dat.calc_var]) not in dat.no_var:
                var = self.var_df.at[var_i, calc_df.at[i, dat.calc_var]] 

            logger.debug(f"current index: {i}, current product: {known_substance}")
            if attempt >= len(calc_df): 
                raise Exception(f"Cannot process {known_substance}. Breaking to prevent infinite loop")

            if known_substance in lup.lookup_var_dict:
                known_substance = self.var_df.at[var_i, 
                lup.lookup_var_dict[known_substance]['lookup_var']] 
            if unknown_substance in lup.lookup_var_dict:
                unknown_substance = self.var_df.at[var_i, 
                lup.lookup_var_dict[unknown_substance]['lookup_var']] 

            if known_substance in io_dicts[known_io]:
                pass
            elif unknown_substance in io_dicts[unknown_io]:
                invert = True
                known_substance, unknown_substance = (unknown_substance, 
                                                      known_substance)
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

            qty_known = io_dicts[known_io][known_substance]
            kwargs = dict(qty=qty_known, 
                          var=var, 
                          known_substance=known_substance, 
                          unknown_substance=unknown_substance, 
                          invert=invert, 
                          emissions_dict=io_dicts['e'],)
            logger.debug(f"Attempting {calc_type} calculation for {unknown_substance} using {qty} of {known_substance}")
            qty_calculated = calc.calcs_dict[calc_type](**kwargs)
            io_dicts[unknown_io][unknown_substance] += qty_calculated

            calc_df = calc_df.drop(i)
            calc_df = calc_df.reset_index(drop=True)
            attempt = 0
            logger.debug(f"{qty_calculated} of {unknown_substance} calculated. {len(calc_df)} calculations remaining.")

        for substance, qty in io_dicts['e'].items(): #add emissions dictionary to outflow dictionary
            io_dicts['o'][substance] += qty

        logger.debug(f"{self.name} process balanced on {qty} of {product}")
        logger.debug('Inflows:')
        for substance, qty in io_dicts['i'].items():
            logger.debug(f"{substance}: {qty}")
        logger.debug('Outflows:')
        for substance, qty in io_dicts['o'].items():
            logger.debug(f"{substance}: {qty}")

        return io_dicts['i'], io_dicts['o']