# -*- coding: utf-8 -*-
""" Data input and output manipulation functions

This module contains data manipulation functions used in BlackBlox.py to 
retrieve user input and manipulate it into useable formats, as well as 
functions used in output file generation.

Module Outline:

Input Data Validators & Cleaners
- function: clean_str
- function: if_str
- function: check_for_col
- function: is_energy
Data Frame Constructors
- function: make_df
- function: mass_energy_df
- function: metadata_df
Writers to Files
- function: build_filedir
- function: write_to_excel
- function: format_and_save_plot
- function: plot_annual_flows
Miscellaneous Functions
- nested_dicts

"""

import pandas as pan
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict, OrderedDict
from datetime import datetime
import dataconfig as dat
from bb_log import get_logger
import about

logger = get_logger("IO")


# INPUT DATA VALIDATORS AND CLENAERS

def clean_str(string_to_check, str_to_cut=False, lower=True, remove_dblnewline=True):
    """Multipurpose function to clean user input strings
    
    Used to clean user input. First creates a copy of the string to prevent 
    the original string from being modified unintentionally.

    Args:
        string_to_check (str): The string to strip and lower
        str_to_cut (str/list/bool): If passed a string, will check for and 
            remove the cut_str string from the string_to_check. If passed a list 
            of strings, will check for and remove each from the string_to_check.
            (Defaults to False.)
        remove_dblnewlines (bool): If True, looks for and removes instances
            of double new lines.
            (Defaults to True.)

    Returns
        The input string, stripped of leading and trailing white space 
        and in all lowercase.

    """

    string = ''.join(string_to_check)

    string = string.strip()
    
    if lower is True:
        string = str.lower(string)

    if type(str_to_cut) is str:
        string = string.replace(str_to_cut, '')
    if type(str_to_cut) is list:
        for snip in str_to_cut:
            string = string.replace(snip, '')

    if remove_dblnewline is True:
        if '\n\n' in string:
            string = string.replace('\n\n', '\n')

    return string


def if_str(maybe_a_string):
    """checks if an input is a string, returns string if so, None if not.

    Args:
        string: a thing to check if it's a string.
    
    Returns:
        The string, if it was a string, otherwise returns None.

    """

    if type(maybe_a_string) is str:
        return maybe_a_string
    else:
        return None


def check_for_col(df, col, index):
    """ Checks if a column exists and returns column value at the given index 

    This function is used mostly to check for whether a column for excel
    worksheet data exists in a particular data location list data frame.

    Args:
        df (pandas.dataframe): The data frame to check
        col (str): the column name to check for
        index (str or int): the row index to get column value for, if column
            exists.

    Returns:
        Value at index, column in the dataframe, if column exists, otherwise
        returns None

    """

    if col in df:
        if type(df.loc[index, col]) is str:
            return df.loc[index, col]

    return None


def is_energy(string, energy_strings=dat.energy_flows):
    """is_energy(string, energy_strings=dat.energy_flows)
    checks if a string refers to an energy flow

    Args:
        string(str): the string to check
        energy_strings(list): list of strings that mark whether the substance
            name that starts or ends with them is an energy flow.
    Returns:
        bool. True, if the string starts or ends with the energy marker. Otherwise, False.
    
    """

    clean_string = clean_str(string)
    is_it_energy = False
    for string in energy_strings:
        if clean_string.startswith(string) or clean_string.endswith(string):
            is_it_energy = True
        
    return is_it_energy


# DATA FRAME CONSTRUCTORS 

def make_df(data, sheet=None, sep='\t', index=0, metaprefix = "meta", 
            col_order = False, T = False, drop_zero=False, sort=False, 
            lower_cols=False, fillna=True):
    """ Creates a Pandas dataframe from various file types

    Numbers that are initially read as strings will be converted to 
    numeric values when possible (errors are ignored).

    Args:
        data: accepts both objects that can be made into dataframes 
            (e.g. nested) dictionaries and strings of filespaths (including 
            excel workbooks, comma seperated value files, and other delimited 
            text files)
        sheet (str, optional): The worksheet of a specified excel workbook. 
            (Defaults to None)
        sep (str): the seperator used in non-csv text file. 
            (Defaults to tab (\t))
        index (int or None): the column of data that is the index. 
            (Defaults to 0)
        metaprefix (str/None): If a column name or row index begins with
            the metaprefix, that row or column is dropped from the data frame.
            (Defaults to 'meta')
        col_order (list[str]/False): If a list is passed, will use those strings
            as the column names of the dataframe in the order in the list.
        T (bool): If True, transposes the data frame before return.
            (Defaults to False)
        drop_zero (bool): If True, converts any NaNs to zeros, and then 
            removes any rows or columns that contain only zeros.
        sort (bool): Whether to sort the data by the ascending order of the
            index
        lower_cols (bool): If true, will convert the column names to all lower case
            (Defaults to False)
        fillna (bool): If true, will convert NaNs to zeros.
            (Defualts to True)

    Returns:
        The generated dataframe.

    """

    if isinstance(data, pan.DataFrame):
        df = data
    elif not isinstance(data, str): 
        df = pan.DataFrame(data)
    elif data.endswith(('.xls', 'xlsx')):
        df = pan.read_excel(data, sheet_name=sheet, index_col=index)
    elif data.endswith('.csv'):
        df = pan.read_csv(data, sep=',', index_col=index)
    else:
        df = pan.read_csv(data, sep=sep, index_col=index) 
                 
    if metaprefix is not None:
        if index is not None:
            df = df[~df.index.str.startswith(metaprefix)]
        cols = [col for col in list(df) if not col.startswith(metaprefix)]
        df = df[cols]

    if type(col_order) is list:
        df = df[col_order]
 
    df = df.apply(pan.to_numeric, errors = 'ignore') #if it looks like a number, make it a number

    if T is True:
        df = df.T

    if drop_zero is True:
        df = df.fillna(0)
        df = df.loc[:, (df != 0).any(axis=0)]
        df = df[np.square(df.values).sum(axis=1) != 0] # uses square so that negative numbers aren't an issue

    if sort is True:
        df.sort_index()

    if lower_cols is True:
        df.columns = [clean_str(c) for c in df.columns]

    if fillna is True:
        df = df.fillna(0)

    return df


def mass_energy_df(df, energy_strings=dat.energy_flows, totals=True, units=dat.default_units):
    """Reorders dataframe to seperate mass and energy flows

    Uses a list of prefix/suffixes to identify mass and energy flows
    and reorders a dataframe to seperate them, orders them alphabetically,
    and also optionally adds rows for mass totals and energy totals.

    Args:
        energy_strings (list): contains strings of prefix/suffix to substance
            names that indicate an energy flow
            (Defaults to dat.energy_flows)
        totals (bool): Appends summation rows for mass and energy seperately.
            (Defaults to True)
        units (dict): dictionary with keys of "mass" and "energy", and
            values for what the units used for each of those are
    """
    logger.debug(f"seperating mass and energy flows using {energy_strings} as energy flow markers")

    cols = list(df)

    mass_df = pan.DataFrame(columns=cols)
    energy_df = pan.DataFrame(columns=cols)

    for i, row in df.iterrows():
        clean_i = clean_str(i)
        energy_flow = False
        for string in energy_strings:
            if clean_i.startswith(string) or clean_i.endswith(string):
                energy_flow = True
                break
        if energy_flow is True:
            energy_df = energy_df.append(row)
        else:
            mass_df = mass_df.append(row)

    if not mass_df.empty:
        mass_df['index-lowercase'] = mass_df.index.str.lower()
        mass_df.sort_values(['index-lowercase'], axis=0, ascending=True, inplace=True)
        del mass_df['index-lowercase']
    if not energy_df.empty:
        energy_df['index-lowercase'] = energy_df.index.str.lower()
        energy_df.sort_values(['index-lowercase'], axis=0, ascending=True, inplace=True)
        del energy_df['index-lowercase']

    if totals is True:
        if not mass_df.empty:
            mass_df = mass_df.append(mass_df.sum().rename(f'TOTAL MASS, in {units["mass"]}'))
        if not energy_df.empty:
            energy_df = energy_df.append(energy_df.sum().rename(f'TOTAL ENERGY, in {units["energy"]}'))

    combined_df = pan.concat([mass_df, energy_df], keys=['Mass', 'Energy'])

    return combined_df
    

def metadata_df(user=dat.user_data, about=about.about_blackblox, name="unknown", level="unknown", 
                product="unknown", product_qty="unknown", scenario="unknown",
                energy_flows=dat.energy_flows, units = dat.default_units):
    """Generates a metadata dataframe for use in excel file output
    """
    
    if is_energy(product):
        product_type = 'energy'
    else:
        product_type = 'mass'
              
    creation_date = datetime.now().strftime("%A, %d %B %Y at %H:%M")
    energy_flows = ', '.join(energy_flows)

    meta = {"00": f"This data was calculated using {about['name']} v{about['version']}",
            "01": f"{about['name']} was created by {about['creator']} of {about['affiliation']}",
            "02": f"More information on {about['name']} can be found at {about['url']}",
            "03": " ",
            "04": " ",
            "05": f"This file was generated on {creation_date}",
            "06": f"by {user['name']} of {user['affiliation']}",
            "07": f"for use in {user['project']}",
            "08": f"and contains {level}-level results data for {name}",
            "09": f"balanced on {product_qty} {units[product_type]} of {product} using the variable values from the {scenario} scenario(s).",
            "10": f"Mass quantites are given in {units['mass']} and energy quantities in {units['energy']}",
            "11": " ",
            "12": f"Note: Substances beginning or ending with any of the following strings were assumed by {about['name']} to be energy flows:",
            "13": f"{energy_flows}",
            "14": " ",
            "15": " ",
            "16": f"{about['name']} is a python package that faciliates the calculation of mass and energy balances for black block models at an arbitrary level of detail.",
            "17": f"For full documentation on how to use {about['name']}, visit {about['documentation_url']}",
            "18": f"{about['name']} is currently under active development. Head over to {about['github_url']} to download, fork, or contribute.",
            "19": f"{about['name']} is avaiable for use free of charge under the terms and conditions of the {about['license']} license.",
    }

    meta_df = pan.DataFrame.from_dict(meta, orient='index', columns=['Workbook Information'])

    meta_df.index = sorted(meta_df.index.values)

    logger.debug(f"metadata dataframe created for {level}-level {name}")

    return meta_df


# WRITERS TO FILES

def build_filedir(filedir, subfolder=None, file_id_list=[], time=True):
    """ Builds complicated file directory names.
    Used for allowing file to be output to unique directories.

    Args:
        filedir (str): the base file directory
        subfolder (str): optional subfolder(s)
            (Defaults to None.)
        file_id_list (list of str): list of strings to append to the directory
            name. 
            (Defaults to an empty list.)
        time (bool): Whether to include a date-time stamp in the file
            directory  name. 
            (Defaults to True.)

    Returns:
        The built file directory string.
    """
    if subfolder is not None:
        filedir=f'{filedir}/{subfolder}'
    
    for file_id in file_id_list:
        if file_id:
            filedir = f'{filedir}_{file_id}'

    if time is True:
        filedir = f'{filedir}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

    return filedir


def write_to_excel(df_or_df_list, sheet_list=None, filedir=dat.outdir, 
                   filename='output'):
    """Writes one or more data frames to a single excel workbook.

    Each data frame appears on its own worksheet. Automatically creates the
    specified output folder if it does not exist.

    args:
        df_or_df_list (dataframe or list): A single pandas dataframe or list
            of pandas dataframes.
        sheet_list (optional, list): List of sheetnames that will be used for
            the dataframe at the same index in df_or_df_list. 
            (Defaults to None.)
        filedir (optional, str): desired file output directory. 
            (Defaults to current working directory.)
        filename (optional, str): desired excel file name, without extension.
            (Defaults to 'output')
    """
    Path(filedir).mkdir(parents=True, exist_ok=True) 

    logger.debug(f"attempting to create {filename} in {filedir}")

    empty_notice = {'00': "The supplied dataframe was empty.",
                    '01': "This could happen is all the supplied values were zero",
                    '02': 'and rows with all zeros were dropped when the data frame was created.'}
    empty_df = pan.DataFrame.from_dict(empty_notice, orient='index', columns=['Empty Dataframe'])

    if isinstance(df_or_df_list, pan.DataFrame):
        df_or_df_list.to_excel(filedir+'/'+filename+'.xlsx')
    
    else:
        with pan.ExcelWriter(filedir+'/'+filename+'.xlsx') as writer:
            for i, df in enumerate(df_or_df_list):
                if sheet_list:
                    sheet = sheet_list[i]
                else:
                    sheet = i
                if df.empty:
                    empty_df.to_excel(writer, sheet)
                else:
                    df.to_excel(writer, sheet)
                logger.debug(f"writing {sheet} sheet to workbook")

    logger.debug(f"{filename} successfully created in {filedir}")


def format_and_save_plot(filepath):
   plt.style.use('tableau-colorblind10')
   plt.grid(True)
   plt.savefig(f"{filepath}.png", format='png', dpi=300)
   plt.savefig(f"{filepath}.svg", format='svg')


def plot_annual_flows(df_dict, flow, outdir, unit_dict=dat.default_units):
    """
    Generated a line plot for each column of a dataframe, using the index
    as the x-axis labels.
    """
    flow_series = []
    for df_name in df_dict:
        if 'cumulative' in df_name:
            pass
        else:
            df = df_dict[df_name].fillna(0)
            if flow in df:
                s = df.loc[:,flow]
                s = s.rename(df_name)
                flow_series.append(s)
    
    flow_df = pan.concat(flow_series, axis=1, sort=True)
    df_index = flow_df.index.tolist()

    energy_flow = is_energy(flow)
    if energy_flow is True:
        flow_unit = unit_dict['energy']
    else:
        flow_unit = unit_dict['mass']

    flow_df.plot(title=f"annual outflows of {flow}")
    plt.xticks(list(range(len(df_index))), df_index, rotation=90)
    plt.ylabel(f"{flow_unit} {flow}")

    format_and_save_plot(f'{outdir}/{flow}')
   
   
# MISCELLANEOUS FUNCTIONS

def nested_dicts(levels=2, final=float):
    """Created a nested defaultdict with an arbitrary level depth

    Example:
        1_level_dict[1st] = final (Same as standard defaultdict)
        2_level_dict[1st][2nd] = final
        4_level_dict[1st][2nd][3rd][4th] = final

    source: https://goo.gl/Wq5kLq

    Args:
        levels (int): The number of nested levels the dictionary should have.
            Defaults to 2. (As 1 is just a normal defaultdict)
        final (type): The type of data stored as the value in the ultimate 
            level of the dictionary.
            Defaults to float because that's what most commonly used in
            this package.

    Returns:
        A nested defaultdict of the specified depth.
    """
    return (defaultdict(final) if levels <2 else
            defaultdict(lambda: nested_dicts(levels - 1, final)))

