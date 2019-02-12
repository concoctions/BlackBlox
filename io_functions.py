# -*- coding: utf-8 -*-
""" Data input and output manipulation functions

This module contains data manipulation functions used in BlackBlox.py to 
retrieve user input and manipulate it into useable formats, as well as 
functions used in output file generation.

"""

import pandas as pan
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import dataconfig as dat


def make_df(data, sheet=None, sep='\t', index=0, metaprefix = "meta", 
            T = False, drop_zero=False):
    """ Creates a Pandas dataframe from various file types

    Numbers that are initially read as strings will be converted to 
    numeric values when possible (errors are ignored).

    Args:
        data: accepts both objects that can be made into dataframes 
            (e.g. nested) dictionaries and strings of filespaths (including 
            excel workbooks, comma seperated value files, and other delimited 
            text files)
        sheet (str, optional): The worksheet of a specified excel workbook. 
            (Defaults to None.)
        sep (str): the seperator used in non-csv text file. 
            (Defaults to tab (\t).)
        index (int or None): the column of data that is the index. 
            (Defaults to 0.)
        metaprefix (str or None): If a column name or row index begins with
            the metaprefix, that row or column is dropped from the data frame.
            (Defaults to 'meta'.)
        T (bool): If True, transposes the data frame before return.
            (Defaults to False.)
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

    if isinstance(df_or_df_list, pan.DataFrame):
        df_or_df_list.to_excel(filedir+'/'+filename+'.xlsx')
    
    else:
        with pan.ExcelWriter(filedir+'/'+filename+'.xlsx') as writer:
            for i, df in enumerate(df_or_df_list):
                if sheet_list:
                    sheet = sheet_list[i]
                else:
                    sheet = i
                df.to_excel(writer, sheet)


def sl(string_to_check):
    """trims a string of surroudning white space and lowers any capitals
    
    Used to clean user input. First creates a copy of the string to prevent 
    the original string from being modified unintentionally.

    Args:
        string_to_check (str): The string to strip and lower

    Returns
        The input string, stripped of leading and trailing white space 
        and in all lowercase.
    """
    string = ''.join(string_to_check)

    string = string.strip()
    string = str.lower(string)

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


