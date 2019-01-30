from molmass import Formula
from collections import defaultdict
from IOfunctions import makeDF
from BBconfig import *
import logging


# shared functions
def checkQty(qty, fraction = False):
    """
    Checks whether the given quantity is within the required ranges.
    Currently, negative numbers are not supported. 
    Seriously, you can't have negative masses here; this isn't quantum.
    """
    if qty < O:
        raise Exception('quantity should be > 0. Currently: {}'.format(qty))
    
    if fraction == True:
        if qty > 1:
            raise Exception('quantity should be between 0 and 1. Currently: {}'.format(qty))

# class Calculation():
#     def __init__(self, known, knownQty, unknown):     
#         if knownQty < 0:
#             print("Error: quantity must be >= 0.")
#             return False
#         self.known = known
#         self.qty = knownQty
#         self.unknown = unknown


# CALCULATION FUNCTIONS

def Ratio(qty, ratio, invert = False):
    """
    The Ratio function calculates a value based on a known value and a given ratio between the known and unknown value:
    Y = qty_X * ratio(Y:X)

    If inversion is selected (invert == True), then it will invert the given ratio before calculation.
    This is used when the opposite quantity is known than what the original ratio is meant for.
    X = qty_Y * (ratio X:Y)
    """

    logging.info("Attempting ratio calcuation using qty: {}, ratio: {}, invert{}".format(qty, ratio, invert))

    checkQty(qty)
    checkQty(ratio)

    if invert == True:
        ratio = 1/ratio

    return qty * ratio


def Remainder(qty, ratio, invert = False):
    """ 
    The Remainder function is to be used when the known quantity and unknown quantity are fractions of a total
    and the fraction of the known quantity is known, and the unknown quantity makes up the remainder of the total.
    Y = qty_X * (1 - ratio[Y:X])

    If inversion is selected (invert == True), then it will invert the given ratio before calculation.
    This is used when the opposite quantity is known than what the original ratio is meant for.
    X = qty_Y * (1 = ratio[X:Y])
    """

    logging.info("Attempting remainder calcuation using qty: {}, ratio: {}, invert{}".format(qty, ratio, invert))

    checkQty(qty)
    checkQty(ratio, fraction = True)

    ratioRemaining = 1 - ratio

    if invert == True:
        return qty / ratioRemaining
    
    else:
        return qty * ratioRemaining

def MolMassRatio(known, qty, unknown):
    """
    Molecultar Mass Ratio Calculation

    Y = qty * (MolMass[X] / MolMass[Y])
    """
    logging.info("Attempting mol mass ratio calcuation using {} ({}) and {}".format(known, qty, unknown))

    return qty * (Formula(self.unknown).mass / Formula(self.known).mass)


def Combustion(known, qty, unknown, combustEff, emissionsDict = False):
    """
    Combustion Calculation", 
    For a given mass or energy quantity of fuel, calculates and return the other
    This function can write CO2 and waste heat emissions to a given emission dictionary, if provided.
    Requires 'df_fuels' lookup dictionary to exist, with an index of the fuel name, and columns for 'HHV', and 'CO2.
    """
    logging.info("Attempting combustion calcuation for {} using qty {} of {} and efficiency of {}".format(unknown, qty, known, combustEff))

    if known not in df_fuels.index and unknown not in df_fuels.index:
        raise Exception("Neither {} nor {} is a known fuel type".format(known, unknown))

    if known in df_fuels.index and unknown in df_fuels.index:
        raise Exception("Both {} and {} are known fuel types.".format(known, unknown))

    checkQty(combustEff, fraction = True)

    #calculates energy and emissions from given mass quantity of fuel
    if known in df_fuels.index:
        fuelType = known
        fuelQty = qty
        energyQty = qty * df_fuels.at[fuelType, 'HHV'] * combustEff
        returnQty = energyQty

    #calculates fuel mass and emissions from given quantity of energy
    else:
        fuelType = unknown
        energyQty = qty
        fuelQty = energyQty / df_fuels.at[fuelType, 'HHV'] * (1/combustEff)
        returnQty = fuelQty

        
    CO2emitted = df_fuels.at[fuelType, 'CO2'] * fuelQty
    wasteHeat = energyQty * (1 - combustEff)

    if type(emissionsDict) defaultdict:
        emissionsDict['CO2'] += CO2emitted
        emissionsDict['waste heat'] += wasteHeat
    
    else:
        logging.info("Emission Data discarded: \n \
            CO2: {}, waste heat: {}".format(CO2emitted, wasteHeat))

    return returnQty

#Calculation Type lookup dictionary
CalculationTypes = {
    'Ratio': Ratio,
    'Remainder': Remainder,
    'MolMassRatio': MolMassRatio,
    'Combustion': Combustion
}