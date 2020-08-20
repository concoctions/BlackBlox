# -*- coding: utf-8 -*-
""" Calculator functions used in balancing unit processes

This module contains the functions used to perform the mass and energy balances
in the unit processes. The calculation type specified by the user in their 
calculation files must be of one of the type specified here, as noted in calc_dict, 
or one defined by the user in custom_lookup.py

Note 1: The "invert" option throughout the calculation is used to allow the unit 
processes to balance regardless of whether the quantity of the "known" or "unknown"
substance is available.

Note 2: the use of **kwargs in the function argument calls is required to 
allow the functions to work properly, since all possible calculator variables  
are provided to the calculator function in unitprocess.py, whether or
not they are used by that specific function.

Module Outline:
- function: check_qty
- function: no_nan
- function: div_no_zero

- function: Ratio
- function: Remainder
- function: ReturnValue
- function: MolMassRatio
- function: Subtraction
- function: Addition
- function: lookup_ratio
- function: Combustion
- function: check_balance

- module variable: calcs_dict
- module variable: twoQty_calc_list 
- module variable: lookup_var_calc_list

"""

from math import isnan
import numpy as np
import pandas as pan
from molmass import Formula
from collections import defaultdict
import blackblox.io_functions as iof
import blackblox.dataconfig as dat
from blackblox.bb_log import get_logger
from blackblox.frames import df_fuels

logger = get_logger("Calculators")
logger.info("Logger for calculators.py initalized")



# DATA CHECK FUNCTIONS
def check_qty(qty, fraction = False):
    """Checks that a quantity is a number, > 0, and optionally < 1.

    Args:
        qty (float or int): number to check
        fraction (bool): whether the number should be between 0 and 1
            (Defaults to False.)
    """

    if not isinstance(qty, (float, int, complex, np.integer, np.floating)):
        raise ValueError(f'quantity should be an int or float. Currently: {type(qty)}')

    if round(qty, dat.float_tol) < 0:
        raise ValueError(f'quantity should be > 0. Currently: {qty}')
    
    if fraction is True:
        if qty > 1:
            raise ValueError(f'quantity should be between 0 and 1. Currently: {qty}')


def no_nan(number):
    """If number is nan, converts it to zero

    Args:
        number: [non-]quantity to check

    Returns:
        If the number is a nan, returns 0. Else returns the input number.
    """

    if number is not None:
        if type(number) not in [str, bool]:
            if isnan(number):
                number = 0
                logger.debug("number converted from nan to 0" )
        elif number == 'nan':
            number = 0
        
    return number


def div_no_zero(qty1, qty2):
    """Prevents divide by zero errors by returning zero if either 
    qty1 or qty2 is zero or nan

    Args:
        qty1 (float or int): The dividend
        qty2 (float or int): The divisor

    Returns: 
        If either qty1 or qty2 is 0 or NaN, returns 0. Else returns the quotient.
    """

    if 0 in [qty1, qty2]:
        return 0
    elif isnan(qty1) or isnan(qty2):
        return 0
    else:
        return qty1/qty2


# CALCULATION FUNCTIONS
def Ratio(qty, var, invert = False, **kwargs):
    """ Multiplies or divides a quantity by a given ratio.
    The invert feature of this function is used by unitprocess.py's
    balance function to allow unit processes to be calculated 
    regardless of whether it is an inflow or outflow that is known.

    Args:
        qty: The known quantity
        var: The ratio of unknown:known quantities
        invert (Bool): Converts the ratio to 1/ratio. (Default is False.)

    Returns:
        float: The input quantity multipled by the [inverted] ratio.

    Examples:
            >>> Ratio(5, 3)
            15

            >>> Ratio(5, 3, invert=True)
            1.6666666666666665
    """

    logger.debug("using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    check_qty(qty)
    check_qty(var)

    if invert is True:
        var = div_no_zero(1,var)

    return (qty * var)


def Remainder(qty, var, invert = False, **kwargs):
    """ Multiplies a quantity by (1 - var). 

    The Remainder function is used by the balance function of unitprocesses.py
    for calculations where the ratio is an inverse of another known ratio. 
    (such as with efficiencies (e.g. product + loss will always equal 100%). 
    The ratio of X:Y and Y:X should always equal 1.0.

    Args:
        qty: The known quantity
        var: The ratio of known:total quantities. A number between 0 and 1,
            where 1-var is the ratio of unknown:total.
        invert (bool): True if the ratio is unknown:total. Converts the ratio
            to 1/ratio. 

    Returns:
        float: The qty multipled (or divided) by 1-var.

    Examples:
        >>> Remainder(5, 0.3)
        3.5
        
        >>> Remainder(5, 0.3, invert=True)
        7.142857142857143
    """

    logger.debug("using qty: {}, ratio: {}, invert: {}".format(qty, var, invert))

    check_qty(qty)
    check_qty(var, fraction = True)

    ratioRemaining = 1 - var

    if invert is True:
        return div_no_zero(qty, ratioRemaining)
    
    else:
        return (qty * ratioRemaining)


def ReturnValue(qty, **kwargs):
    """ Returns quantity.

    Useful for creating temporary duplicate values with unique names in the unit 
    process's temporary dictionary if substance of same name exists in both input 
    and output dictionary.

    Args:
        qty: a quantity (or anything really)

    Returns:
        qty: literally the exact thing you gave it.

    Examples:
        >>> ReturnValue(5)
        5
    """
    check_qty(qty)
    return (qty)


def MolMassRatio(known_substance, qty, unknown_substance, var=1.0, invert=False, **kwargs):
    """Calculates a quantity using the molar mass ratio to a substance with known quantity
    
    Args:
        known_substance (str): The chemical formula of the substance of known quantity, 
        qty: The quantity of the known substance
        unknown_substance (str): The chemical formula of the substance of unknown quantity.
        var (float): The number of mols of the unknpwn substance per mol of known substance
            (Defaults to 1.0)

    Returns:
        float: The qty of the unknown substance, determined by multiplying qty the ratio
        of the molecular weights of unknown:known substances.

    Example:
        >>> MolMassRatio('CaCO3', 5, 'CO2')
        2.198564447495127

        >>> MolMassRatio('C8H10N4O2', 5, 'C12H22O11')
        8.81341527344784
        
    """
    logger.debug("using {} of {} to determine qty of {}".format(qty, known_substance, unknown_substance))

    if var is None or var in dat.no_var:
        var = 1.0

    if invert is True:
        var = 1/var

    check_qty(qty)
    return qty * (Formula(unknown_substance).mass / Formula(known_substance).mass) *  var


def Subtraction(qty, qty2, invert = False, **kwargs):
    """Subtracts one quantity from another.

    By default, that qty is the minuend and qty2 is the subtrahend. 
    Returns the difference = qty - qty2.

    If invert is True, qty is the subtrahend and qty2 is the difference.
    Returns the minuend = qty + qty2

    Args:
        qty (float): The quantity of a known substance
        qty2 (float): The quantity of another known substance
        invert: If True, adds rathers the values rather than subtracts them.
            (Defaults to False)

    Returns:
        float: The quantity of a third substance. 

    """
    logger.debug("using qty: {}, qty2: {}, invert: {}".format(qty, qty2, invert))

    check_qty(qty)
    check_qty(qty2)

    if invert is False:
        return_qty = (qty) - (qty2)
    else:
        return_qty = (qty) + (qty2)

    check_qty(return_qty) 
    return return_qty


def Addition(qty, qty2, invert = False, **kwargs):
    """Adds one quantity to another.

    By default, qty and qty2 are the addends and returns the sum = qty + qty2

    If invert is True, qty is the sum and qty2 is an addent and returns the 
    remaining addend = qty - qty2


    Args:
        qty (float): The quantity of a known substance
        qty2 (float): The quantity of another known substance
        invert: If True, subtracts rathers the values rather than adds them.
            (Defaults to False)

    Returns:
        float: The quantity of a third substance

    """
    logger.debug("using qty: {}, qty2: {}, invert: {}".format(qty, qty2, invert))

    check_qty(qty)
    check_qty(qty2)
    
    if invert is False:
        return_qty = (qty) + (qty2)
    else:
        return_qty = (qty) - (qty2)    

    check_qty(return_qty)
    return return_qty


def lookup_ratio(known_substance, qty, unknown_substance, var=None, lookup_df=df_fuels, **kwargs):
    """Ratio function, but for lookup DataFrames

    If the known_substance is in the index of the dataframe, multiples qty
    by the ratio found in the var column of the dataframe.

    If the unknown_substance is in the index of the dataframe, divides qty
    by the ratio found in the var column of the dataframe.

    Only one of known and unknown substances can be in the dataframe index.


    Args:
        known_substance (str): name of the known quantity
        qty (float): quantity of known substance
        unknown_substance (str): name of the unknown quantity
        var (str): The relevant column in the lookup dataframe
        lookup_df (DataFrame): dataframe with lookup data
            (defaults to fuels dataframe)
    Returns:
        float

    """
    logger.debug(f"using dataframe {lookup_df.columns}, {qty} of {known_substance} and {var} for {unknown_substance}")

    check_qty(qty)

    if (iof.no_suf(known_substance) not in lookup_df.index and iof.no_suf(unknown_substance) not in lookup_df.index):
        raise Exception("Neither {} nor {} is in the specified lookup dataframe".format(known_substance, unknown_substance))

    if (iof.no_suf(known_substance) in lookup_df.index and iof.no_suf(unknown_substance) in lookup_df.index):
        raise Exception("Both {} and {} are are both in the lookup dataframe.".format(known_substance, unknown_substance))

    if iof.no_suf(known_substance) in lookup_df.index:
        substance = iof.no_suf(known_substance)
        return_qty = (qty) * (lookup_df.at[substance, var.lower()])

    else:
        substance = iof.no_suf(unknown_substance)
        return_qty = div_no_zero(qty, lookup_df.at[substance, var.lower()])
        
        logger.debug(f"{return_qty} of {unknown_substance} derived from {qty} of {known_substance} using {var} ratio")

    check_qty(return_qty)
    return return_qty


def Combustion(known_substance, qty, unknown_substance, var=1.0, 
               emissions_list = dat.default_emissions, emissions_dict=False, 
               inflows_dict=False, fuels_df=df_fuels, LHV=True, 
               write_energy_in=True, **kwargs):
    """Specicalized multi-lookup function for energy content and emissions of fuel combustion.

        Args:
        known_substance (str): name of the known quantity, either 
            a fuel named in fuels_df or the name of the related energy flow
        qty (float): quantity of known substance
        unknown_substance (str): name of the unknown quantity, either
            a fuel named in fuels_df or the name of the related energy flow
        var (float): the combustion efficiency (Between 0 and 1).
            (Defaults to 1)
        emissions_list (list[str]): List of emissions to calculate, if emission
            factors are available in the fuel dataframe
            (Defaults to dat.default_emissions)
        emissions_dict (defaultdict or bool): If provided, the dictionary where 
            calculated emission quantities will be written. 
            (Defaults to False)
        inflows_dict (defaultdict or bool): If provided, the dictionary where the
            calculated oxygen required for combustion will be written.
            (Defaults to False)
        fuels_df (dataframe): Dataframe containing the fuel name as index ('fuel_type'), 
            and columns with heating values ('lhv' or 'hhv'), and emission ratios (as
            kg emission/kg fuel in column named as the emission type).
            (Defaults to df_fuels)
        LHV (bool): If True, uses the lower heating value of the fuel. If False,
            uses the higher heating value of the fuel, as specified in 'lhv' and 'hhv'
            columns of the fuels_df, respectively.
            (Defaults to True)
        
    Returns:
        float: The quantity of the unkown substance (fuel or energy)

    Note:
        Only one of known and unknown substances can be in the dataframe index.

        Emission data is not returned, but added to the specified emission dictionary.
        Besides the specified emissions, it will also calculate "waste heat" based on 
        the combustion efficiency.

        If an inflow dictionary is specified, "O2 needed for combustion" will be
        calculated and added to it, based on the the difference between the 
        calculated emissions and the fuel mass.
    
    Examples:
        >>> Combustion('charcoal', 3, 'heat', 0.8)
        72.0

        >>> Combustion('heat', 3, 'charcoal', 0.8)
        0.125
 


    """
    logger.debug(f"using {qty} of {known_substance} and efficiency of {var} to calculate {unknown_substance}")
    logger.debug(f"using dataframe with columns {fuels_df.columns}")

    if (iof.no_suf(known_substance) not in fuels_df.index 
        and iof.no_suf(unknown_substance) not in fuels_df.index):
        raise Exception("Neither {} nor {} is a known fuel type".format(known_substance, unknown_substance))

    if (iof.no_suf(known_substance) in fuels_df.index 
        and iof.no_suf(unknown_substance) in fuels_df.index):
        raise Exception("Both {} and {} are known fuel types.".format(known_substance, unknown_substance))

    check_qty(qty)

    if var is None or var in dat.no_var:
        combust_eff = 1.0
    else:
        combust_eff = var
    check_qty(combust_eff, fraction=True)

    if LHV is True:
        HV = 'lhv'
    else:
        HV = 'hhv'

    if iof.no_suf(known_substance) in fuels_df.index:
        fuel_type = iof.no_suf(known_substance)
        fuel_qty = (qty)
        energy_qty = qty * (fuels_df.at[fuel_type, HV.lower()]) # total energy in fuel
        return_qty = energy_qty * combust_eff # useful energy after combustion
        logger.debug(f"energy qty ({fuel_type}) calculated at {energy_qty}, of which {return_qty} useful (Eff: {combust_eff}")

    else:
        fuel_type = iof.no_suf(unknown_substance)
        energy_qty = (qty) * ((1/combust_eff)) # total energy in fuel
        fuel_qty = div_no_zero(energy_qty, fuels_df.at[fuel_type, HV.lower()])
        return_qty = fuel_qty
        logger.debug(f"fuel qty ({fuel_type}) calculated at {return_qty}")

    combustion_emissions = dict()
    for emission in emissions_list:
        if emission.lower() in fuels_df:
            combustion_emissions[f'{emission}'] = (fuels_df.at[fuel_type, emission.lower()]) * (fuel_qty)
        else:
            logger.warning(f'{emission} not found for {fuel_type}.')

    if type(emissions_dict) == defaultdict:
        if type(inflows_dict) == defaultdict: #only writes balancing inflow O2 and energy if emissions and waste heat will be added to emission dict.
            inflows_dict[f'O2{dat.ignore_sep}combustion'] += sum(combustion_emissions.values()) - fuel_qty # closes mass balance
            logger.debug(f"{sum(combustion_emissions.values()) - fuel_qty} of O2 added to inflow dict")
            if write_energy_in is True:
                inflows_dict[f'energy in combusted {fuel_type}'] = energy_qty
                logger.debug(f"{energy_qty} of inflow energy added to inflow dict")

        combustion_emissions['waste heat'] = (energy_qty) * (1 - combust_eff) 
        for emission in combustion_emissions:
            emissions_dict[emission] += combustion_emissions[emission]

    logger.debug("Emission Data Calculated:")
    for emission in combustion_emissions:
        logger.debug(f"{emission}: {combustion_emissions[emission]}") 

    check_qty(return_qty)
    return return_qty


def check_balance(inflow_dict, outflow_dict, raise_imbalance=True, 
                  ignore_flows=[], only_these_flows=False, round_n=dat.float_tol):
    """Checks whether inflow and outflow dictionaries sum to same total quantity

    Args:
        inflow_dict (dict/defaultdict): dictionary of inflows with 
            the format inflow_dict[substance name] = quantity
        outflow_dict (dict/defaultdict): dictionary of outflows with
            the format outflow_dict[substance name] = quantity
        round_n (int): Number of places after the decimal to use when checking
            if inflow and outflow masses are equivelent.
            (Defaults to dat.float_tol)
        ignore_flows (list[str]): A list of strings that indicate that a 
            substance is not be included in the balance. If any of the keys in 
            eiher dictionary begin or end with a string in this list, its value 
            will not be added to the total quantity.
            (Defaults to an empty list)
        only_these_flows (bool/list): An optional list of strings. If provided,
            the check will only include keys that begin or end with strings in 
            this list
            (Defaults to False)


    Returns:
        bool: True if the flows are balanced. Otherwise False.
        float: sum of all inflows.
        float: sum of all outflows.

    """

    logger.info("checking whether dictionary value sums balance")

    totals = [0,0]
    flows = [[],[]]

    for i, flow_dict in enumerate([inflow_dict, outflow_dict]):

        for substance, qty in flow_dict.items():
            substance = iof.clean_str(substance)
            ignore = False

            if type(only_these_flows) is list:
                logger.debug(f"Only including flows beginning/ending with {only_these_flows}")
                ignore = True
                for includable in only_these_flows:
                    if substance.startswith(includable) or substance.endswith(includable):
                        ignore = False

            logger.debug(f"Ignoring flows beginning/ending with {ignore_flows}")
            for ignorable in ignore_flows:
                if substance.startswith(ignorable) or substance.endswith(ignorable):
                    ignore = True
            
            if ignore is True: 
                logger.debug(f'{substance} ({qty}) discarded')
            if ignore is False:
                logger.debug(f'{substance} ({qty}) included')
                totals[i] += (qty)
                flows[i].append(substance)

    total_in = round(totals[0], round_n)
    total_out = round(totals[1], round_n)

    if raise_imbalance is True:
        if total_in != total_out:
            raise ValueError(f'IMBALANCED! Total In:  {total_in} v Total Out: {total_out}')

    else:
        logger.debug(f"Total Inflow:  {totals[0]}")
        logger.debug(f"Total Outflow: {totals[1]}")
        logger.debug(f"Inflows:  {flows[0]}")
        logger.debug(f"Outflows: {flows[1]}")

    return total_in, total_out


calcs_dict = {
    'ratio': {'function': Ratio, 'kwargs': {}},
    'remainder': {'function': Remainder, 'kwargs': {}},
    'molmassratio': {'function': MolMassRatio, 'kwargs': {}},
    'returnvalue': {'function': ReturnValue, 'kwargs': {}},
    'subtraction': {'function': Subtraction, 'kwargs': {}},
    'addition': {'function': Addition, 'kwargs': {}},
    'energycontent-lhv': {'function': lookup_ratio, 'kwargs': {'lookup_df': df_fuels, 'var':'lhv'}},
    'energycontent-hhv': {'function': lookup_ratio, 'kwargs': {'lookup_df': df_fuels, 'var':'hhv'}},
    'energycontent':{'function': lookup_ratio, 'kwargs': {'lookup_df': df_fuels, 'var':'lhv'}},
    'combustion': {'function': Combustion, 'kwargs': {}},
    'combustion-noenergyin': {'function': Combustion, 'kwargs': {'write_energy_in':False}},
    'combustion-lhv': {'function': Combustion, 'kwargs': {'LHV':True}},
    'combustion-lhv-noenergyin': {'function': Combustion, 'kwargs': {'LHV':True, 'write_energy_in':False}},
    'combustion-hhv': {'function': Combustion, 'kwargs': {'LHV':False}},
    'combustion-hhv-noenergyin': {'function': Combustion, 'kwargs': {'LHV':False, 'write_energy_in':False}},
    'lookupratio': {'function': lookup_ratio, 'kwargs': {}},
    'lookupratio-fuels': {'function': lookup_ratio, 'kwargs': {'lookup_df': df_fuels}},
}
"""Names of calculation types available for the use in calculation tables.
The keys in this dictionary should be all lowercase.
Must be manually updated if additional calculators are added to this module. 

Used by the Unit Process class's balance function.

"""

twoQty_calc_list = ['subtraction', 'addition']
"""List of calculations that require two quantities to exist in the unit process flow dictionary.

Used by the Unit Process class's balance function.
"""

lookup_var_calc_list = ['lookupratio', 'lookupratio-fuels', 'energycontent-lhv', 'energycontent', 'energycontent-hhv']
"""List of calculations where the specified variable is for the lookup df, and not the unit process variable df
"""
