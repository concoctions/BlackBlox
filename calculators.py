from molmass import Formula
from collections import defaultdict
from io_functions import make_df
from bb_log import get_logger

import dataconfig as dat

logger = get_logger("Calculators")

# shared functions
def check_qty(qty, fraction = False):
    """
    Checks whether the given quantity is within the required ranges.
    Currently, negative numbers are not supported. 
    Seriously, you can't have negative masses here; this isn't quantum.
    """
    if qty < 0:
        raise ValueError(f'quantity should be > 0. Currently: {qty}')
    
    if fraction == True:
        if qty > 1:
            raise ValueError(f'quantity should be between 0 and 1. Currently: {qty}')


# CALCULATION FUNCTIONS

def Ratio(qty, var, invert = False, **kwargs):
    """
    var: Ratio of unknown_substance quantity to known_substance quantity
    The Ratio function calculates a value based on a known_substance value and a given ratio between the known_substance and unknown_substance value:
    Y = X * ratio(Y:X)

    If inversion is selected (invert == True), then it will invert the given ratio before calculation.
    This is used when the opposite quantity is known_substance than what the original ratio is meant for.
    X = Y * (ratio X:Y)
    """

    logger.debug("Attempting ratio calcuation using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    check_qty(qty)
    check_qty(var)

    if invert == True:
        var = 1/var

    return qty * var


def Remainder(qty, var, invert = False, **kwargs):
    """ 
    var: Ratio of known_substance quantity to total
    The Remainder function is to be used when the known_substance quantity and unknown_substance quantity are fractions of a total
    and the fraction of the known_substance quantity is known_substance, and the unknown_substance quantity makes up the remainder of the total.
    Y = X * (1 - ratio[X:[X+Y]])

    If inversion is selected (invert == True), then it will invert the given ratio before calculation.
    This is used when the opposite quantity is known_substance than what the original ratio is meant for.
    X = Y / (1 - ratio[X:X+Y])
    """

    logger.debug("Attempting remainder calcuation using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    check_qty(qty)
    check_qty(var, fraction = True)

    ratioRemaining = 1 - var

    if invert == True:
        return qty / ratioRemaining
    
    else:
        return qty * ratioRemaining

def ReturnValue(qty, **kwargs):
    """
    Returns the value passed as the qty argument. Useful for creating temporary
    values with unique names in the unit process's temporary dictionary if
    substance of same name exists in both input and output dictionary.
    """
    return qty

def MolMassRatio(known_substance, qty, unknown_substance, **kwargs):
    """
    Molecular Mass Ratio Calculation

    Y = X * (MolMass[X] / MolMass[Y])
    """
    logger.debug("Attempting mol mass ratio calcuation using {} ({}) and {}".format(known_substance, qty, unknown_substance))

    return qty * (Formula(unknown_substance).mass / Formula(known_substance).mass)


def Combustion(known_substance, qty, unknown_substance, var, emissions_dict=False, fuels_dict=dat.df_fuels, **kwargs):
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

    check_qty(var, fraction = True)

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

#Calculation Type lookup dictionary
calcs_dict = {
    'ratio': Ratio,
    'remainder': Remainder,
    'molmassratio': MolMassRatio,
    'combustion': Combustion,
    'returnvalue': ReturnValue
}