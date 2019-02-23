# -*- coding: utf-8 -*-
""" Data input and output manipulation functions

This module contains data manipulation functions used in BlackBlox.py to 
retrieve user input and manipulate it into useable formats, as well as 
functions used in output file generation.

Module Outline:
- imports
- function: make_df
- function: check_for_col
- function: build_filedir
- function: write_to_excel
- fucntion: sl
- function: if_str
- function: nested_dicts

"""

import pandas as pan
import numpy as np
from pathlib import Path
from collections import defaultdict, OrderedDict
from datetime import datetime
import dataconfig as dat
from bb_log import get_logger

logger = get_logger("IO")


def make_df(data, sheet=None, sep='\t', index=0, metaprefix = "meta", 
            col_order = False, T = False, drop_zero=False):
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

    return df


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


def mass_energy_df(df, energy_strings=dat.energy_flows, totals=True):
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

    mass_df.index = sorted(mass_df.index.values, key=lambda s: s.lower())
    energy_df.index = sorted(energy_df.index.values, key=lambda s: s.lower())

    if totals is True:
        mass_df = mass_df.append(mass_df.sum().rename('TOTAL - mass'))
        energy_df = energy_df.append(energy_df.sum().rename('TOTAL - energy'))

    combined_df = pan.concat([mass_df, energy_df], keys=['Mass', 'Energy'])

    return combined_df
    
def metadata_df(user=dat.user_data, name="unknown", level="unknown", 
                product="unknown", product_qty="unknown", var_i="unknown",
                energy_flows=dat.energy_flows):
    
    BB = {"name": "BlackBlox.py",
          "version": "0.1",
          "URL": "Offline Only",
          "documentation": "Offline Only",
          "github": "Offline Only",
          "creator": "S.E. Tanzer",
          "affiliation": "TU Delft",
          "license": "GPL v3"
                  }
              
    creation_date = datetime.now().strftime("%A, %d %B %Y at %H:%M")
    energy_flows = ', '.join(energy_flows)

    meta = {"00": f"This data was calculated using {BB['name']} v{BB['version']}",
            "01": f"{BB['name']} was created by {BB['creator']} of {BB['affiliation']}",
            "02": f"More information on {BB['name']} can be found at {BB['URL']}",
            "03": " ",
            "04": " ",
            "05": f"This file was generated on {creation_date}",
            "06": f"by {user['name']} of {user['affiliation']}",
            "07": f"for use in {user['project']}",
            "08": f"and contains {level}-level results data for {name}",
            "09": f"balanced on {product_qty} of {product} using the variable values from the {var_i} scenario(s)",
            "10": " ",
            "11": f"Note: Substances beginning or ending with any of the following strings were assumed by {BB['name']} to be energy flows:",
            "12": f"{energy_flows}",
            "13": " ",
            "14": " ",
            "15": f"{BB['name']} is a python package that faciliates the calculation of mass and energy balances for black block models at an arbitrary level of detail.",
            "16": f"For full documentation on how to use {BB['name']}, visit {BB['documentation']}",
            "17": f"{BB['name']} is currently under active development. Head over to {BB['github']} to download, fork, or contribute.",
            "18": f"{BB['name']} is avaiable for use free of charge under the terms and conditions of the {BB['license']} license.",
    }

    meta_df = pan.DataFrame.from_dict(meta, orient='index', columns=['Workbook Information'])

    meta_df.index = sorted(meta_df.index.values)

    logger.debug(f"metadata dataframe created for {level}-level {name}")

    return meta_df


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


def clean_str(string_to_check, str_to_cut=False, remove_dblnewline=True):
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


