from collections import defaultdict

import io_functions as iof
import dataconfig as dat

from bb_log import get_logger

logger = get_logger("Custom Lookup")

# lookup variables for unit processcalculations table (replaces variable with specific value from variable file)
# lookup_var is the keyword string in calc file to trigger lookup: (dataframe of lookup data, column name in variable table to replace with) 
# LOOK UP VARIABLES
lookup_var_dict = { 
    'fuel': dict(data_frame=iof.make_df(dat.lookup_var_file, sheet='Fuels'), 
                 lookup_var='fuelType'),
    } 

# LOOKUP VARIABLES DICTIONARY SHORTCUT NAMES
df_fuels = lookup_var_dict['fuel']['data_frame']


# CUSTOM FUNCTIONS
def Combustion(known_substance, qty, unknown_substance, var, emissions_dict=False, fuels_dict=df_fuels, **kwargs):
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


# CUSTOM CALCULATORS DICTIONARY (will be added to standard calculators dictionary)
custom_calcs_dict = {
    'combustion': Combustion,
}