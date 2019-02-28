# -*- coding: utf-8 -*-
""" Custom "lookup" substances and related functions

This module is the place to put special substance names that should not
be used as-is, but "looked up" in the unit process variables table. 
Optionally, the substance name can have a data frame associated with it
that contains further data about the substances, such as may be used in
any custom calculators.

Additionally, this is the place for custom calculator functions, such 
as those that manipulate the look-up variables or otherwise perform more 
than just standard mathetmatical operations. Besideds adding the function
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

Module Outline:
- imports and logger
- module variable: lookup_var_dict (dict)
- module variables for custom fuel combustion functions
    - df_fuels (dataframe)
    - default_emissions_list (list)
    - fuel_composition

- function: Combustion
- module variable: custom_calcs_dict (dict)


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

# LOOK UP DATA FRAMES
df_fuels = iof.make_df(dat.lookup_var_file, sheet='Fuels')

# LOOK UP VARIABLES
lookup_var_dict = { 
    'fuel': dict(data_frame=df_fuels, 
                 lookup_var='fuelType'),
    'fossil fuel': dict(data_frame=df_fuels, 
                 lookup_var='fossil fuel type'),
    'biofuel': dict(data_frame=df_fuels, 
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

# OTHER CUSTOM VARIABLES

# default_fuel_composition = ['C', 'H', 'O', 'S', 'N', 'moisture', 'ash']


# CUSTOM FUNCTIONS
def Combustion(known_substance, qty, unknown_substance, var, 
               emissions_dict=False, inflows_dict=False, 
               emissions_list = ['CO2', 'H2O', 'SO2'], fuels_df=df_fuels, 
               **kwargs):
    """Calculates fuel or energy quantity and combustion emissions

    This is a function designed to calculate the quantity of fuel 
    necessary to generate a certain quantity of energy, or the quantity
    of energy generated by combusting a given quantity of fuel. It requires
    the existence of a dataframe with the HHV of the given fuel. 

    It can also calculate the emission of combustion, if relevent factors are
    present in the fuel dataframe, and output that data to a outflows dictionary 
    (e.g that of the unit process calling the function). 

    Note:
    Besides the listed emissions, it will also calculate "waste heat" based on 
    the combustion efficiency. 

    To maintain mass balances, the difference between the combustion emissions
    and the fuel mass is added to the inflows dictionary (if specified) as 
    'O2' (oxygen). To calculate non-oxygen-based combustion emissions and
    co-inflows, instead use the "stoichiometric_combustion" function, which
    requires the elemental composition of the fuel.
    

    Examples:
        >>> Combustion('charcoal', 3, 'heat', 0.8)
        72.0

        >>> Combustion('heat', 3, 'charcoal', 0.8)
        0.125
 
    Args:
        known_substance (str): The name of the known substance, either a solid
            fuel or an energy flow. If the string is not in the index of the 
            fuels dataframe, known_substance is assumed to be the energy
            output of the combusted fuel.
        qty (float): the quantity of the known substance (mass or energy)
        unknown_substance (str): The name of the unknown substance, either a 
            solid fuel or an energy flow. If the string is not in the index of 
            the fuels dataframe, known_substance is assumed to be the energy
            output of the combusted fuel.
        var (float): the efficiency of combustion (Between 0 and 1).
        emissions_dict (defaultdict/bool): The destination dictionary where to 
            store the calculated combustions emissions data. If no dictionary
            is provided, emission data will not be stored.
            (Defaults to False)
        inflows_dict (defaultdict/bool): The destination dictionary where to
            store the calculated combustion co-inputs data. If no dictionary
            is provided, co-inputs data will not be stored. Currently the only
            co-input considered is oxygen.
            (Defaults to False)
        emissions_list (list[str]): List of emissions to calculate, if emission
            factors are available in the fuel dataframe
            (Defaults to default_emission_list, defined above.)
        fuels_df (dataframe): The dataframe containing the names, HHVs,
            and emissions data of the fuel.
            (Defaults to df_fuels)
        
    Returns:
        float: The quantity of the unkown substance (fuel or energy)

    """
    logger.debug("Attempting combustion calcuation for {} using qty {} of {} and efficiency of {}".format(unknown_substance, qty, known_substance, var))

    if (known_substance not in fuels_df.index 
        and unknown_substance not in fuels_df.index):
        raise Exception("Neither {} nor {} is a known_substance fuel type".format(known_substance, unknown_substance))

    if (known_substance in fuels_df.index 
        and unknown_substance in fuels_df.index):
        raise Exception("Both {} and {} are known_substance fuel types.".format(known_substance, unknown_substance))

    if var is None:
        var = 1.0
    if var < 0 or var > 1:
        raise ValueError(f'quantity should be between 0 and 1. Currently: {qty}')

    if known_substance in fuels_df.index:
        fuel_type = known_substance
        fuel_qty = qty
        energy_qty = qty * fuels_df.at[fuel_type, 'HHV'] * var
        return_qty = energy_qty

    else:
        fuel_type = unknown_substance
        energy_qty = qty
        fuel_qty = energy_qty / fuels_df.at[fuel_type, 'HHV'] * (1/var)
        return_qty = fuel_qty

    combustion_emissions = dict()
    for emission in emissions_list:
        if emission in fuels_df:
            combustion_emissions[emission] = fuels_df.at[fuel_type, emission] * fuel_qty
    waste_heat = energy_qty * (1 - var)

    if type(emissions_dict) == defaultdict:
        for emission in combustion_emissions:
            emissions_dict[emission] += combustion_emissions[emission]
        if type(inflows_dict) == defaultdict:
            inflows_dict['O2'] += sum(emissions_dict.values()) - fuel_qty

        emissions_dict['waste_heat'] += waste_heat
    
    else:
        logger.debug("Emission Data discarded:")
        for emission in combustion_emissions:
            logger.debug(f"{emission}: {combustion_emissions[emission]}")
        logger.debug(f"waste_heat: {waste_heat}")

    return return_qty

# UNFINISHED
# def stoichiometric_combustion(known_substance, qty, unknown_substance, var, 
#                               emissions_dict=False, inflows_dict=False, 
#                               fuels_df=df_fuels, **kwargs):
#     """Combustion function that calculates emissions stoichiometrically

#     This function calls the Combustion function to calculate the energy
#     or fuel quantity, but then uses the 
#     """

#     return_qty = Combustion(known_substance, qty, unknown_substance, var,
#                             emissions_dict=False, inflows_dict=False,
#                             fuels_df=fuels_df)

#     if known_substance in fuels_df.index:
#         fuel_type = known_substance
#         fuel_qty = qty
#         energy_qty = return_qty
#     else:
#         fuel_type = unknown_substance
#         fuel_qty = return_qty
#         energy_qty = qty

#     combustion_emissions = dict()

#     # INSERT STOICHIOMETRIC EMISSIONS CALCULATIONS HERE

#     waste_heat = energy_qty * (1 - var)

#     if type(emissions_dict) == defaultdict:
#         for emission in combustion_emissions:
#             emissions_dict[emission] += combustion_emissions[emission]        
#         if type(inflows_dict) == defaultdict:
#             inflows_dict['O2'] += fuel_qty - sum(emissions_dict.values())
        
#         emissions_dict['waste heat'] += waste_heat
    
#     else:
#         logger.debug("Emission Data discarded:")
#         for emission in combustion_emissions:
#             logger.debug(f"{emission}: {combustion_emissions[emission]}")
#         logger.debug(f"waste heat: {waste_heat}")

#     return return_qty

    


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