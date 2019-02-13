# -*- coding: utf-8 -*-
""" Custom "lookup" substances and related functions

This module is the place to put special substance names that should not
be used as-is, but "looked up" in the unit process variables table. 
Optionally, the substance name can have a data frame associated with it
that contains further data about the substances, such as may be used in
any custom calculators.

Additionally, this is the place for custom calculator functions, such 
as those that manipulate the look-up variables or perform more than
just standard mathetmatical operations.  Besideds adding the function
definition, be sure to add the function name to the dictionary at the 
bottom of the moduel, so the function will be added to the BlackBlox
calculator dictionary.

When building functions, please note unitprocess.py will provide the 
following standard arguments. If not all of these are used in the 
function, be sure to allow the function to accept **kwargs to avoid
raising a KeyError.
    qty:
    var:
    known_substance:
    unknown_subtance: 

Currently this file contains the following:

Custom lookup variables:
fuel: allows fuel type to be specified per scenario. With data frame.

Custom calculator functions:
Combustion: calculates combustion emissions from qty of energy or fuel mass

"""

from collections import defaultdict

import io_functions as iof
import dataconfig as dat

from bb_log import get_logger

logger = get_logger("Custom Lookup")
 
# LOOK UP VARIABLES
lookup_var_dict = { 
    'fuel': dict(data_frame=iof.make_df(dat.lookup_var_file, sheet='Fuels'), 
                 lookup_var='fuelType'),
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
            below. NOT USED DIRECTLY BY BLACKBLOX.PY.
"""

# LOOKUP VARIABLES SHORTCUT NAMES
df_fuels = lookup_var_dict['fuel']['data_frame']


# CUSTOM FUNCTIONS
def Combustion(known_substance, qty, unknown_substance, var, 
               emissions_dict=False, fuels_dict=df_fuels, **kwargs):
    """
    Combustion Calculation", 
    var: Efficiency of combustion
    For a given mass or energy quantity of fuel, calculates and return the other
    This function can write CO2 and waste heat emissions to a given emission dictionary, if provided.
    Requires 'df_fuels' lookup dictionary to exist, with an index of the fuel name, and columns for 'HHV', and 'CO2.
    """
    logger.debug("Attempting combustion calcuation for {} using qty {} of {} and efficiency of {}".format(unknown_substance, qty, known_substance, var))

    if known_substance not in fuels_dict.index and unknown_substance not in fuels_dict.index:
        raise Exception("Neither {} nor {} is a known_substance fuel type".format(known_substance, unknown_substance))

    if known_substance in fuels_dict.index and unknown_substance in fuels_dict.index:
        raise Exception("Both {} and {} are known_substance fuel types.".format(known_substance, unknown_substance))

    if var < 0 or var > 1:
        raise ValueError(f'quantity should be between 0 and 1. Currently: {qty}')

    #calculates energy and emissions from given mass quantity of fuel
    if known_substance in fuels_dict.index:
        fuel_type = known_substance
        fuel_qty = qty
        energy_qty = qty * fuels_dict.at[fuel_type, 'HHV'] * var
        return_qty = energy_qty

    #calculates fuel mass and emissions from given quantity of energy
    else:
        fuel_type = unknown_substance
        energy_qty = qty
        fuel_qty = energy_qty / fuels_dict.at[fuel_type, 'HHV'] * (1/var)
        return_qty = fuel_qty

        
    CO2emitted = fuels_dict.at[fuel_type, 'CO2'] * fuel_qty
    wasteHeat = energy_qty * (1 - var)

    if type(emissions_dict) == defaultdict:
        emissions_dict['CO2'] += CO2emitted
        emissions_dict['waste heat'] += wasteHeat
    
    else:
        logger.debug("Emission Data discarded: \n \
            CO2: {}, waste heat: {}".format(CO2emitted, wasteHeat))

    return return_qty


# CUSTOM CALCULATORS DICTIONARY 
custom_calcs_dict = {
    'combustion': Combustion,
}

"""Dictionary of custom calculator functions

The functions in this dictionary will be added to the calculation type
lookup dictionary created in calculators.py and used by the unitprocess.py
to calculate 

    key (str): the (lowered) string used to identify the calculation type,
        used in the unit process calculation tables. Should be unique, 
        including not repeating 
    value: The associated function
"""