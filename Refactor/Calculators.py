from molmass import Formula
from collections import defaultdict
from IOfunctions import makeDF
from BBconfig import *
import logging

logging.basicConfig(filename='refactor.log',level=logging.DEBUG)

# shared functions
def checkQty(qty, fraction = False):
    """
    Checks whether the given quantity is within the required ranges.
    Currently, negative numbers are not supported. 
    Seriously, you can't have negative masses here; this isn't quantum.
    """
    if qty < 0:
        raise Exception('quantity should be > 0. Currently: {}'.format(qty))
    
    if fraction == True:
        if qty > 1:
            raise Exception('quantity should be between 0 and 1. Currently: {}'.format(qty))


# CALCULATION FUNCTIONS

def Ratio(qty, var, invert = False, **kwargs):
    """
    var: Ratio of unknown quantity to known quantity
    The Ratio function calculates a value based on a known value and a given ratio between the known and unknown value:
    Y = X * ratio(Y:X)

    If inversion is selected (invert == True), then it will invert the given ratio before calculation.
    This is used when the opposite quantity is known than what the original ratio is meant for.
    X = Y * (ratio X:Y)
    """

    logging.info("Attempting ratio calcuation using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    checkQty(qty)
    checkQty(var)

    if invert == True:
        var = 1/var

    return qty * var


def Remainder(qty, var, invert = False, **kwargs):
    """ 
    var: Ratio of known quantity to total
    The Remainder function is to be used when the known quantity and unknown quantity are fractions of a total
    and the fraction of the known quantity is known, and the unknown quantity makes up the remainder of the total.
    Y = X * (1 - ratio[X:[X+Y]])

    If inversion is selected (invert == True), then it will invert the given ratio before calculation.
    This is used when the opposite quantity is known than what the original ratio is meant for.
    X = Y / (1 - ratio[X:X+Y])
    """

    logging.info("Attempting remainder calcuation using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    checkQty(qty)
    checkQty(var, fraction = True)

    ratioRemaining = 1 - var

    if invert == True:
        return qty / ratioRemaining
    
    else:
        return qty * ratioRemaining

def MolMassRatio(known, qty, unknown, **kwargs):
    """
    Molecultar Mass Ratio Calculation

    Y = X * (MolMass[X] / MolMass[Y])
    """
    logging.info("Attempting mol mass ratio calcuation using {} ({}) and {}".format(known, qty, unknown))

    return qty * (Formula(unknown).mass / Formula(known).mass)


def Combustion(known, qty, unknown, var, emissionsDict = False, **kwargs):
    """
    Combustion Calculation", 
    var: Efficiency of combustion
    For a given mass or energy quantity of fuel, calculates and return the other
    This function can write CO2 and waste heat emissions to a given emission dictionary, if provided.
    Requires 'df_fuels' lookup dictionary to exist, with an index of the fuel name, and columns for 'HHV', and 'CO2.
    """
    logging.info("Attempting combustion calcuation for {} using qty {} of {} and efficiency of {}".format(unknown, qty, known, var))

    if known not in df_fuels.index and unknown not in df_fuels.index:
        raise Exception("Neither {} nor {} is a known fuel type".format(known, unknown))

    if known in df_fuels.index and unknown in df_fuels.index:
        raise Exception("Both {} and {} are known fuel types.".format(known, unknown))

    checkQty(var, fraction = True)

    #calculates energy and emissions from given mass quantity of fuel
    if known in df_fuels.index:
        fuelType = known
        fuelQty = qty
        energyQty = qty * df_fuels.at[fuelType, 'HHV'] * var
        returnQty = energyQty

    #calculates fuel mass and emissions from given quantity of energy
    else:
        fuelType = unknown
        energyQty = qty
        fuelQty = energyQty / df_fuels.at[fuelType, 'HHV'] * (1/var)
        returnQty = fuelQty

        
    CO2emitted = df_fuels.at[fuelType, 'CO2'] * fuelQty
    wasteHeat = energyQty * (1 - var)

    if type(emissionsDict) == defaultdict:
        emissionsDict['CO2'] += CO2emitted
        emissionsDict['waste heat'] += wasteHeat
    
    else:
        logging.info("Emission Data discarded: \n \
            CO2: {}, waste heat: {}".format(CO2emitted, wasteHeat))

    return returnQty

#Calculation Type lookup dictionary
CalculationTypes = {
    'ratio': Ratio,
    'remainder': Remainder,
    'molmassratio': MolMassRatio,
    'combustion': Combustion
}