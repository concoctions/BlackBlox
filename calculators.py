# -*- coding: utf-8 -*-
""" Calculator functions used in balancing unit processes

This module contains the standard set of functions used to manipulate the 
quantites specified in the user data. The calculation type specified by the 
user must be of one of the type specified here, as noted in calc_dict, or one 
defined by the user in custom_lookup.py

The "invert" option throughout the calculation helps the unit processes to 
balance processes balance on an arbitrary known quantity even though
the user is specifying only a single-directional relationship between substance
quantities in the relationships table.

Note, the use of **kwargs in the function argument calls is required to 
allow the functions to work properly, since all possible calculatr variables  
are provided to the calculator function in unitprocess.py, whether or
not they are used by that specific function.

Module Outline:
- module variable: df_fuels
- function: check_qty
- function: Ratio
- function: Remainder
- function: ReturnValue
- function: MolMassRatio
- function: Subtraction
- function: Addition
- function: check_balance
- function: Energy_Content
- function: lookup_ratio
- module variable: calcs_dict
- module variable: twoQty_calc_list 
- module variable: lookup_var_calc_list

"""

import pandas as pan
from molmass import Formula
from collections import defaultdict
import io_functions as iof
import dataconfig as dat
from bb_log import get_logger

logger = get_logger("Calculators")

# LOOKUP DATA NEEDED BY CALCULATORS
df_fuels = None
"""Dataframe of data regarding different fuel types.
This should include at minimum: the LHV and CO2 emissions of the fuel.
Generated if 'fuel' is in dat.lookup_var_dict
"""

if 'fuel' in dat.lookup_var_dict: 
    df_fuels = iof.make_df(dat.lookup_var_dict['fuel']['filepath'], sheet=dat.lookup_var_dict['fuel']['sheet'])


# INPUT CHECKER FUNCTIONS
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
        invert (Bool): Specify True if the ratio is known:unknown. Converts the 
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
        invert (bool): True if the ratio is unknown:total. Converts the ratio
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


def Subtraction(qty, qty2, invert = False, **kwargs):
    """Subtracts one quantity from another.

    Assuming the known values are X and X1, returns Y = X - X1.
    If invert is True, then assumes that the known values are Y and X1, and 
    returns X = Y + X1

    Args:
        qty (float): The quantity of a known substance
        qty2 (float): The quantity of another known substance
        invert: If True, adds rathers the values rather than subtracts them.
            (Defaults to False)

    Returns:
        float: The quantity of a third substance

    """
    if invert is False:
        return qty - qty2

    else:
        return qty + qty2

def Addition(qty, qty2, invert = False, **kwargs):
    """Adds one quantity to another.

    Assuming the known values are X and X1, returns Y = X + X1.
    If invert is True, then assumes that the known values are Y and X1, and 
    returns X = Y - X1

    Args:
        qty (float): The quantity of a known substance
        qty2 (float): The quantity of another known substance
        invert: If True, subtracts rathers the values rather than adds them.
            (Defaults to False)

    Returns:
        float: The quantity of a third substance

    """
    
    if invert is False:
        return qty + qty2

    else:
        return qty - qty2    



def check_balance(inflow_dict, outflow_dict, raise_imbalance=True, 
                  ignore_flows=[], only_these_flows=False, round_n=5):
    """Checks whether two dictionary mass values sum to equivelent quantities 

    Used to check whether the inflows and outflows of a unit process are
    balanced. Takes dictionaries of inflows and outflows with substance names
    as keys and quantities as values. Optionally can use a list of substance name 
    prefix/suffix tags to exclude flows (e.g. energy flows in a mass balance), or
    only include certain flows (e.g. only include those with the energy tag)

    Args:
        inflow_dict (dict/defaultdict): the dictionary of inflows with 
            the format inflow_dict[substance name] = quantity
        outflow_dict (dict/defaultdict): the dictionary of outflows with
            the format outflow_dict[substance name] = quantity
        round_n (int): Number of places after the decimal to use when checking
            if inflow and outflow masses are equivelent.
            Defaults to 5.
        ignore_flows (list[str]): A list of strings that indicate that a 
            substance is not be included in the balance. If any of the keys in 
            he inflow_dict or outflow_dict begin or end with a string in the 
            ignore_flows list, the substance will not be added to the total 
            quantity.
            (Defaults to an empty list)
        only_these_flows (bool/list): if given a list of strings, will only
            include those flows that begin or end with the strings in this

    Returns:
        bool: True if the mass flows are balanced. Otherwise False.
        float: sum of all mass inflows.
        float: sum of all mass outflows.

    """

    totals = [0,0]
    flows = [[],[]]

    for i, flow_dict in enumerate([inflow_dict, outflow_dict]):

        for substance, qty in flow_dict.items():
            substance = iof.clean_str(substance)
            ignore = False

            if type(only_these_flows) is list:
                ignore = True
                for includable in only_these_flows:
                    if not substance.startswith(includable):
                        logger.debug(f'{substance} not includable; {qty} discarded from inflows')
                        ignore = False
                        break
                    elif not substance.endswith(includable):
                        logger.debug(f'{substance} not includable; {qty} discarded from inflows')
                        ignore = False
                        break
                    
            for ignorable in ignore_flows:
                if substance.startswith(ignorable):
                    logger.debug(f'{substance} ignorable; {qty} discarded from inflows')
                    ignore = True
                    break
                elif substance.endswith(ignorable):
                    logger.debug(f'{substance} ignorable; {qty} discarded from inflows')
                    ignore = True
                    break

            if ignore is False:
                totals[i] += qty
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


def Energy_Content(known_substance, qty, unknown_substance, LHV=True, fuels_df=df_fuels, **kwargs):
    """
    Returns the energy value of a requested fuel quantity or the fuel
    quantity, when provided an energy value of a requested fuel

    Args:
        known_substance (str): name of the known quantity, either 
            a fuel in fuels_df or the name of that fuel's energy flow
        qty (float): quantity of known substance
        unknown_substance (str): name of the unknown quantity, either
            the fuel or enery flow
        LHV (bool): If True, uses the LHV heating value. If False, used
            the HHV.
            (Defaults to False)
        fuels_df: data frame with fuels data

    Returns:
        float: energy quantity if the the known substance was a fuel, or fuel
            quantity, if the known substance was an energy content

    """
    if (known_substance.split(dat.ignore_sep)[0] not in fuels_df.index and unknown_substance.split(dat.ignore_sep)[0] not in fuels_df.index):
        raise Exception("Neither {} nor {} is a known_substance fuel type".format(known_substance, unknown_substance))

    if (known_substance.split(dat.ignore_sep)[0] in fuels_df.index and unknown_substance.split(dat.ignore_sep)[0] in fuels_df.index):
        raise Exception("Both {} and {} are known_substance fuel types.".format(known_substance, unknown_substance))

    if LHV is True:
        HV = 'lhv'
    else:
        HV = 'hhv'

    if known_substance.split(dat.ignore_sep)[0] in fuels_df.index:
        fuel_type = known_substance.split(dat.ignore_sep)[0]
        fuel_qty = qty
        energy_qty = qty * fuels_df.at[fuel_type, HV] # total energy in fuel
        return_qty = energy_qty # useful energy after combustion

    else:
        energy_qty = qty
        fuel_type = unknown_substance.split(dat.ignore_sep)[0]
        fuel_qty = energy_qty / fuels_df.at[fuel_type, HV]
        return_qty = fuel_qty
        
        logger.debug(f"{return_qty} of {unknown_substance} derived from {qty} of {known_substance}")

    return return_qty


def lookup_ratio(known_substance, qty, unknown_substance, var=None, lookup_df=df_fuels, force_df=False, **kwargs):
    """Ratio function, but for lookup DataFrames
    Multiplies or divides a quantity by a given ratio, based on data in a
    dataframe that is not the unit's var_df. Note that only ONE of the known
    and unknown substances can be in the lookup DatFrame index


    Args:
        known_substance (str): name of the known quantity
        qty (float): quantity of known substance
        unknown_substance (str): name of the unknown quantity
        var (str): The variable (column) to use from the  lookup table
        lookup_df (DataFrame): data frame with lookup data
        force_df (DataFrame or bool): force the use of a specific data frame,
            even if the substance names lookup keys would cause another one

    Returns:
        float

    """

    if isinstance(force_df, pan.DataFrame):
        lookup_df = force_df

    logger.debug(f"using dataframe {lookup_df.columns}")

    if (known_substance.split(dat.ignore_sep)[0] not in lookup_df.index and unknown_substance.split(dat.ignore_sep)[0] not in lookup_df.index):
        raise Exception("Neither {} nor {} is in the specified lookup dataframe".format(known_substance, unknown_substance))

    if (known_substance.split(dat.ignore_sep)[0] in lookup_df.index and unknown_substance.split(dat.ignore_sep)[0] in lookup_df.index):
        raise Exception("Both {} and {} are are both in the lookup dataframe.".format(known_substance, unknown_substance))

    if known_substance.split(dat.ignore_sep)[0] in lookup_df.index:
        substance = known_substance.split(dat.ignore_sep)[0]
        return_qty = qty * lookup_df.at[substance, var.lower()]

    else:
        substance = unknown_substance.split(dat.ignore_sep)[0]
        return_qty = qty / lookup_df.at[substance, var.lower()]
        
        logger.debug(f"{return_qty} of {unknown_substance} derived from {qty} of {known_substance} using {var} ratio")

    return return_qty


def Combustion(known_substance, qty, unknown_substance, var, 
               emissions_dict=False, inflows_dict=False, 
               emissions_list = dat.default_emissions, fuels_df=df_fuels, 
               LHV=True, write_energy_in=True, **kwargs):
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
    the combustion efficiency, and "O2 needed for combustion", based on the 
    difference between the fuel mass and the emissions mass

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
    logger.debug(f"using dataframe with columns {fuels_df.columns}")

    if (known_substance.split(dat.ignore_sep)[0] not in fuels_df.index 
        and unknown_substance.split(dat.ignore_sep)[0] not in fuels_df.index):
        raise Exception("Neither {} nor {} is a known_substance fuel type".format(known_substance, unknown_substance))

    if (known_substance.split(dat.ignore_sep)[0] in fuels_df.index 
        and unknown_substance.split(dat.ignore_sep)[0] in fuels_df.index):
        raise Exception("Both {} and {} are known_substance fuel types.".format(known_substance, unknown_substance))

    
    if var is None or var in dat.no_var:
        combust_eff = 1.0
    elif var < 0 or var > 1:
        raise ValueError(f'quantity should be between 0 and 1. Currently: {qty}')
    else:
        combust_eff = var

    if LHV is True:
        HV = 'lhv'
    else:
        HV = 'hhv'

    if known_substance.split(dat.ignore_sep)[0] in fuels_df.index:
        fuel_type = known_substance.split(dat.ignore_sep)[0]
        fuel_qty = qty
        energy_qty = qty * fuels_df.at[fuel_type, HV.lower()] # total energy in fuel
        return_qty = energy_qty * combust_eff # useful energy after combustion

    else:
        fuel_type = unknown_substance.split(dat.ignore_sep)[0]
        energy_qty = qty * (1/combust_eff) # total energy in fuel
        fuel_qty = energy_qty / fuels_df.at[fuel_type, HV.lower()]
        return_qty = fuel_qty

    combustion_emissions = dict()
    for emission in emissions_list:
        if emission.lower() in fuels_df:
            combustion_emissions[f'{emission}{dat.ignore_sep}emitted'] = fuels_df.at[fuel_type, emission.lower()] * fuel_qty
    waste_heat = energy_qty * (1 - combust_eff)

    if type(emissions_dict) == defaultdict:
        if type(inflows_dict) == defaultdict:
            inflows_dict[f'O2{dat.ignore_sep}combustion'] += sum(combustion_emissions.values()) - fuel_qty # closes mass balance
            if write_energy_in is True:
                inflows_dict[f'energy in combusted {fuel_type}'] = energy_qty
        emissions_dict['waste heat'] += waste_heat
        for emission in combustion_emissions:
            emissions_dict[emission] += combustion_emissions[emission]

    logger.debug("Emission Data Calculated:")
    for emission in combustion_emissions:
        logger.debug(f"{emission}: {combustion_emissions[emission]}")
    logger.debug(f"waste_heat: {waste_heat}")

    return return_qty


calcs_dict = {
    'ratio': {'function': Ratio, 'kwargs': {}},
    'remainder': {'function': Remainder, 'kwargs': {}},
    'molmassratio': {'function': MolMassRatio, 'kwargs': {}},
    'returnvalue': {'function': ReturnValue, 'kwargs': {}},
    'subtraction': {'function': Subtraction, 'kwargs': {}},
    'addition': {'function': Addition, 'kwargs': {}},
    'energycontent-lhv': {'function': Energy_Content, 'kwargs': {'LHV':True}},
    'energycontent-hhv': {'function': Energy_Content, 'kwargs': {'LHV': False}},
    'energycontent': {'function': Energy_Content, 'kwargs': {}},
    'combustion': {'function': Combustion, 'kwargs': {}},
    'combustion-noenergyin': {'function': Combustion, 'kwargs': {'write_energy_in':False}},
    'combustion-lhv': {'function': Combustion, 'kwargs': {'LHV':True}},
    'combustion-lhv-noenergyin': {'function': Combustion, 'kwargs': {'LHV':True, 'write_energy_in':False}},
    'combustion-hhv': {'function': Combustion, 'kwargs': {'LHV':False}},
    'combustion-hhv-noenergyin': {'function': Combustion, 'kwargs': {'LHV':False, 'write_energy_in':False}},
    'lookup ratio': {'function': lookup_ratio, 'kwargs': {}},
    'lookup ratio-fuels': {'function': lookup_ratio, 'kwargs': {'force_df': df_fuels}},
}
"""Dictionary of calculators available to process unit process relationships.
The keys in this dictionary should be all lowercase.
Must be manually updated if additional calculators are added to this module. 

Can also be used to create alias names for functions with non-default keyword
arguments that would not be typically passed by the data in calc_df.

Used by the Unit Process class's balance function.

"""

twoQty_calc_list = ['subtraction', 'addition']
"""List of calculations that require two quantities to exist in the unit process flow dictionary.

Used by the Unit Process class's balance function.
"""

lookup_var_calc_list = ['lookup ratio', 'lookup ratio-fuels']
"""List of calculations where the specified variable is for the lookup df, and not the unit process variable df
"""