# -*- coding: utf-8 -*-
""" Calculator functions used in balancing unit processes

This module contains the standard set of functions used to manipulate the 
quantites specified in the user data. The calculation type specified by the 
user must be of one of the type specified here, or one defined by the user in
custom_lookup.py

Note, the use of **kwargs in the function argument calls is required to 
allow the functions to work properly, since all possible calculatr variables  
are provided to the calculator function in unitprocess.py, whether or
not they are used by that specific function.

Module Outline:
- imports and logger
- function: check_qty
- function: Ratio
- function: Remainder
- function: ReturnValue
- function: MolMassRatio
- function: check_balance
- module variable: calcs_dict

"""

from molmass import Formula
from collections import defaultdict
import io_functions as iof
import dataconfig as dat
import custom_lookup as lup
from bb_log import get_logger

logger = get_logger("Calculators")


# FUNCTIONS USED BY CALCUALTOR FUNCTIONS
def check_qty(qty, fraction = False):
    """Checks that a quantity is > 0 and optionally < 1.
    Raises and error if the quantity is negative, and, optionally, if it is 
    less than one. Currently BlackBlox does not support negative masses or
    energy contents. This isn't quantum.

    Args:
        qty (float or int): number to check
        fraction (bool): whether the number should be between 0 and 1
            (Defaults to False.)

    """

    if qty < 0:
        raise ValueError(f'quantity should be > 0. Currently: {qty}')
    
    if fraction is True:
        if qty > 1:
            raise ValueError(f'quantity should be between 0 and 1. Currently: {qty}')


# CALCULATION FUNCTIONS
def Ratio(qty, var, invert = False, **kwargs):
    """ Multiplies or divides a quantity by a given ratio.

    This function exists as it is to allow unit processes to be calculated 
    backwards or forwards. The user only has to specify one relationship
    (e.g. Y:X for a known X), but if it is Y that's known, then it flips
    the ratio to be X:Y.

    Examples:
            >>> Ratio(5, 3)
            15

            >>> Ratio(5, 3, invert=True)
            1.6666666666666665

    Args:
        qty: The known quantity
        var: The ratio of unknown:known quantities
        invert (Bool): Specigy True if the ratio is known:unknown. Converts the 
            ratio to 1/ratio. 
                (Default is False.)

    Returns:
        The original quantity multipled by the ratio.
  
    """

    logger.debug("Attempting ratio calcuation using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    check_qty(qty)
    check_qty(var)

    if invert is True:
        var = 1/var

    return qty * var


def Remainder(qty, var, invert = False, **kwargs):
    """ Multiplies a quantity by the inverse of a known ratio between 0 and 1

    The Remainder function is useful when both the known and unknown quantities
    are two parts of the same total, but the percentage balance may change 
    (such as with efficiencies (product + loss will always equal 100%). 
    The ratio of X:Y and Y:X should always equal 1.0.

    Examples:
        >>> Remainder(5, 0.3)
        3.5
        
        >>> Remainder(5, 0.3, invert=True)
        7.142857142857143

    Args:
        qty: The known quantity
        var: The ratio of known:total quantities. A number between 0 and 1,
            where 1-var is the ratio of unknown:total.
        invert (bool): True if the ratio is unknwon:total. Converts the ratio
            to 1/ratio. 

    """

    logger.debug("Attempting remainder calcuation using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    check_qty(qty)
    check_qty(var, fraction = True)

    ratioRemaining = 1 - var

    if invert is True:
        return qty / ratioRemaining
    
    else:
        return qty * ratioRemaining


def ReturnValue(qty, **kwargs):
    """ Returns the value passed to it.

    Returns the value passed as the qty argument. Useful for creating temporary
    values with unique names in the unit process's temporary dictionary if
    substance of same name exists in both input and output dictionary.

    Examples:
        >>> ReturnValue(5)
        5

    Args:
        qty: a quantity (or anything really)

    Returns:
        qty: literally the exact thing you gave it.
    """
    return qty


def MolMassRatio(known_substance, qty, unknown_substance, **kwargs):
    """Uses the ratio of molecular mass of two substances to 
    
    This function takes the quantity of a known substance and the name of 
    that substance and another which are also valid chemical compositions 
    and uses the ratio of their molecular weights to calculate the quantity 
    of the substance of unknown quantity.

    Example:
        >>> MolMassRatio('CaCO3', 5, 'CO2')
        2.198564447495127

        >>> MolMassRatio('C8H10N4O2', 5, 'C12H22O11')
        8.81341527344784
        

    Args:
        known_substance (str): The name of the substance of known quantity, 
            which must be a valid chemical composition
        qty: The quantity of the known substance
     unknown_substance (str): The name of the substance of unknown quantity,
            which must be a valid chemical composition.

    """
    logger.debug("Attempting mol mass ratio calcuation using {} ({}) and {}".format(known_substance, qty, unknown_substance))

    return qty * (Formula(unknown_substance).mass / Formula(known_substance).mass)

def check_balance(inflow_dict, outflow_dict, raise_imbalance=True, 
                  ignore_flows=dat.massless_flows, round_n=5):
    """Checks whether two dictionary mass values sum to equivelent quantities 

    Used to check whether the inflows and outflows of a unit process are
    balanced. Takes dictionaries of inflows and outflows and removes non-mass 
    flows using a list of strings that indicate that a substance is not mass.
     then sums the remaining values

    Args:
        inflow_dict (dict/defaultdict): the dictionary of inflows with 
            the format inflow_dict[substance name] = quantity
        outflow_dict (dict/defaultdict): the dictionary of outflows with
            the format outflow_dict[substance name] = quantity
        round_n (int): Number of places after the decimal to use when checking
            if inflow and outflow masses are equivelent.
            Defaults to 5.
        not_mass_list (list[str]): A list of strings that indicate that a 
            substance is not mass-based. If any of the keys in the inflow_dict
            or outflow_dict begin or end with a sring in the no_mass_list,
            the substance will not be added to the total mass count.
            (Defaults to dat.massess_flows)

    Returns:
        bool: True if the mass flows are balanced. Otherwise False.
        float: sum of all mass inflows.
        float: sum of all mass outflows.
    """
    total_in = 0
    flows_in = []
    total_out = 0
    flows_out = []

    for substance, qty in inflow_dict.items():
        substance = iof.clean_str(substance)
        ignore = False
            
        for ignorable in ignore_flows:
            if substance.startswith(ignorable):
                logger.debug(f'{substance} not mass; {qty} discarded from inflows')
                ignore = True
                break
            elif substance.endswith(ignorable):
                print(f'{substance} not mass; {qty} discarded from inflows')
                ignore = True
                break

        if ignore is False:
            total_in += qty
            flows_in.append(substance)

    for substance, qty in outflow_dict.items():
        substance = iof.clean_str(substance)
        ignore = False

        for ignorable in ignore_flows:
            if substance.startswith(ignorable):
                logger.debug(f'{substance} not mass; {qty} discarded from outflows')
                ignore = True
                break
            elif substance.endswith(ignorable):
                logger.debug(f'{substance} not mass; {qty} discarded from outflows')
                ignore = True
                break
        
        if ignore is False:
            total_out += qty
            flows_out.append(substance)

    total_in = round(total_in, round_n)
    total_out = round(total_out, round_n)

    if raise_imbalance is True:
        if total_in != total_out:
            raise ValueError(f'IMBALANCED! Total In:  {total_in} v Total Out: {total_out}')

    else:
        logger.debug(f"Total Inflow Mass:  {total_in}")
        logger.debug(f"Total Outflow Mass: {total_out}")
        logger.debug(f"Inflows:  {flows_in}")
        logger.debug(f"Outflows: {flows_out}")

    return total_in, total_out


#Calculation Type lookup dictionary
calcs_dict = {
    'ratio': Ratio,
    'remainder': Remainder,
    'molmassratio': MolMassRatio,
    'returnvalue': ReturnValue
}
"""Dictionary of calculators available to process unit process relationships.
Must be updated if additional calculators are added to this module. 
Automatically pulls in calculators in the custom_lookup module, if they are
specified in the custom_calcs_dict in that module.

Used by the Unit Process class's balance function.

"""

for calc in lup.custom_calcs_dict:  #adds calculators from custom_lookup
    if calc in calcs_dict:
        raise KeyError(f"Function with name {calc} exists in both calculators and custom_lookup. Please use unique function names.")
    else:
        calcs_dict[calc] = lup.custom_calcs_dict[calc]