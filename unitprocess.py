import pandas as pan
from molmass import Formula
from collections import defaultdict

from bb_log import get_logger

import io_functions as iof
import dataconfig as dat
import calculators  as calc


logger = get_logger("Unit Process")


# UNIT PROCESS
class UnitProcess:
    """
    UnitProcess objects have a set of inflows and outflows, with the relationship 
    between them expressed in a DataFrame of calculations and a DataFrame of 
    variables to use in the calculations.

    The sets of inflows and outflows is derived from the list of calculation 
    supplied by the user.

    UnitProcess.balance allows the user to specify a specific quantity of an 
    input and , and a specific set of calculation variables to use, and the 
    function will return dictionaries (defaultdict) of the quantities of the 
    unit process inflows and outflows to balance the given product quantity.
    """

    def __init__(self, name, var_df=False, calc_df=False, 
                units_df=dat.df_unit_library):
        logger.debug(f"creating unit process object for {name}")
        self.name = name

        self.var_df = iof.check_if_df(var_df, 
            alt_data=units_df.at[name, dat.var_filepath])

        self.calc_df = iof.check_if_df(calc_df, 
            alt_data=units_df.at[name, dat.calc_filepath], index=None)

        #create sets of process inflows and outflows
        self.default_product = units_df.at[name, dat.unit_product]
        self.default_io = units_df.at[name, dat.unit_product_io]
        
        self.inflows = set() 
        self.outflows = set() 
        
        for i in self.calc_df.index: 
            products = [ (self.calc_df.at[i, dat.known], 
                str.lower(self.calc_df.at[i, dat.known_io])),
                 (self.calc_df.at[i, dat.unknown],
                 str.lower(self.calc_df.at[i, dat.unknown_io]))]

            for product, i_o in products:
                if i_o.startswith('i'):
                    self.inflows.add(product)
                elif i_o.startswith('o'):
                    self.outflows.add(product)
            
 
    def balance(self, qty, product=False, i_o=False, 
                var_i=False, show=False):
        """
        # product: final input or outflow on which to balance the calculations
        # qty: desired final quantity of product
        # i_o: whether product is an input (i) or outflow (o)
        # var_i: row index of variables files to use
        # show: whether to display the formatted inflows and outflows in the 
        # python terminal
        """

        #verifies arguments
        if product is False:
            product = self.default_product
        if i_o is False:
            i_o = self.default_io
        if var_i is False:
            var_i = dat.default_scenario

        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{product} not found in {self.name} inflows or outflows')

        if var_i not in self.var_df.index.values:
            raise Exception(f'{var_i} not found in variables file')

        if str.lower(i_o[0]) not in ['i', 'o', 't', 'e']:
            raise Exception(f'{i_o} not valid product destination')

        if product in dat.lookup_var_dict:
            product = self.var_df.at[var_i, dat.lookup_var_dict[product]['lookup_var']]   
        
        logger.debug(f"Attempting to balance {self.name} on {qty} of {product} ({i_o}) using {var_i} variables")

        
        #setup function variables
        calc_df = self.calc_df
        io_dicts = {
            'i' : defaultdict(float),    # inflows dictionary
            'o' : defaultdict(float),    # outflows dictionary
            't' : defaultdict(float),    # temp dictionay (discarded values)
            'e' : defaultdict(float)     # emissions dictionary - adds value to outflow dictionary at end of function
        }

        io_dicts[str.lower(i_o[0])][product] = qty
               
        i = 0
        attempt = 0
    

        # perform specified calculations, starting with the known_substance
        while len(calc_df) > 0:
                       
            if i >= len(calc_df):     # if at end of list, loop around
                i = 0

            # setup loop variables
            known_substance = calc_df.at[i, dat.known]
            known_io =str.lower(calc_df.at[i, dat.known_io][0]) # shortens to i, o, or t (lower case)
            unknown_io = str.lower(calc_df.at[i, dat.unknown_io][0]) # shortens to i, o or t (lower case)
            unknown_substance = calc_df.at[i, dat.unknown]
            calc_type = str.lower(calc_df.at[i, dat.calc_type])
            invert = False
            var = False

            if str.lower(calc_df.at[i, dat.calc_var]) not in dat.no_var:
                var = self.var_df.at[var_i, calc_df.at[i, dat.calc_var]] 

            logger.debug(f"current index: {i}, current product: {known_substance}")

            if attempt >= len(calc_df): 
                raise Exception(f"Cannot process {known_substance}. Breaking to prevent infinite loop")

            if known_substance in dat.lookup_var_dict:
                known_substance = self.var_df.at[var_i, 
                dat.lookup_var_dict[known_substance]['lookup_var']] 
            if unknown_substance in dat.lookup_var_dict:
                unknown_substance = self.var_df.at[var_i, 
                dat.lookup_var_dict[unknown_substance]['lookup_var']] 

            if known_substance in io_dicts[known_io]:
                pass
            elif unknown_substance in io_dicts[unknown_io]:
                invert = True
                known_substance, unknown_substance = unknown_substance, known_substance
                known_io, unknown_io = unknown_io, known_io
                logger.debug(f"{known_substance} not found, but {unknown_substance} found. Inverting calculations")
            else:
                i += 1
                attempt += 1
                logger.debug(f"neither {known_substance} nor {unknown_substance} found, skipping for now")
                continue
            
            # performed specified calculation
            
            if calc_type not in calc.calcs_dict:
                raise Exception(f"{calc_type} is an unknown_substance calculation type")

            qty_known = io_dicts[known_io][known_substance]
            kwargs = dict(qty=qty_known, var=var, known_substance=known_substance, 
            unknown_substance=unknown_substance, invert=invert, emissions_dict=io_dicts['e'])

            qty_calculated = calc.calcs_dict[calc_type](**kwargs)

            if unknown_io not in io_dicts:
                raise Exception(f"{unknown_io} is an unknown destination")
            
            io_dicts[unknown_io][unknown_substance] += qty_calculated

            calc_df = calc_df.drop(i)
            calc_df = calc_df.reset_index(drop=True)

            logger.debug(f"{len(calc_df)} calculations remaining.")
            attempt = 0


        #add emissions dictionary to outflow dictionary
        for substance, qty in io_dicts['e'].items():
            io_dicts['o'][substance] += qty


        logger.debug(f"{self.name} process balanced on {qty} of {product}")
        logger.debug('Inflows:')
        for substance, qty in io_dicts['i'].items():
            logger.debug(f"{substance}: {qty}")
        logger.debug('Outflows:')
        for substance, qty in io_dicts['o'].items():
            logger.debug(f"{substance}: {qty}")

        return io_dicts['i'], io_dicts['o']
