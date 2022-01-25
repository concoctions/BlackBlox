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
- function: write_to_xls
- function: format_and_save_plot
- function: plot_annual_flows

Miscellaneous Functions
- nested_dicts

"""
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pan

import blackblox.about as about
from blackblox.dataconfig import bbcfg
from blackblox.bb_log import get_logger


logger = get_logger("IO")


# INPUT DATA VALIDATORS AND CLENAERS


def check_type(thing, is_type=[], not_this=False, not_not=False):
    if type(is_type) is not list:
        is_type = [is_type]

    if type(thing) not in is_type:
        raise TypeError(f"{thing} ({type(thing)}) is not an accepted type ({is_type})")

    if not_this is True:
        if thing in not_this:
            raise ValueError(f"{thing} cannot be any of {not_this}")

    if not_not is True:
        if not thing:
            raise ValueError(f"{thing} must not have a Booleen value of False.")


def clean_str(string_to_check, str_to_cut=False, lower=True, remove_dblnewline=True,
              cut_whole_line_only=False):
    """Multipurpose function to clean user input strings
    
    Used to clean user input. First creates a copy of the string to prevent 
    the original string from being modified unintentionally.

    Args:
        string_to_check (str): The string to strip and lower
        str_to_cut (str/list/bool): If passed a string, will check for and 
            remove the cut_str string from the string_to_check. If passed a list 
            of strings, will check for and remove each from the string_to_check.
            (Defaults to False.)
        cut_whole_line_only (bool): If True, only cuts string if it begins or
            ends with a \n. 
            (Defaults to False)

    Returns
        The input string, stripped of leading and trailing white space 
        and in all lowercase.

    """

    string = ''.join(string_to_check)

    string = string.strip()

    if lower is True:
        string = str.lower(string)

    if type(str_to_cut) is str:
        if cut_whole_line_only is True:
            if string == str_to_cut:
                string = ''
            else:
                string = string.replace(f'{str_to_cut}\n', '')
                string = string.replace(f'\n{str_to_cut}', '')
        else:
            string = string.replace(str_to_cut, '')
    if type(str_to_cut) is list:
        for snip in str_to_cut:
            if cut_whole_line_only is True:
                if string == snip:
                    string = ''
                else:
                    string = string.replace(f'{snip}\n', '')
                    string = string.replace(f'\n{snip}', '')
            else:
                string = string.replace(snip, '')

    if remove_dblnewline is True:
        if '\n\n' in string:
            string = string.replace('\n\n', '\n')

    return string


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
        str value at index, column in the dataframe, if column exists, otherwise
        returns None

    """

    if col in df:
        if type(df.loc[index, col]) is str:
            return df.loc[index, col]

    return None


def is_energy(string, energy_strings=bbcfg.energy_flows):
    """is_energy(string, energy_strings=bbcfg.energy_flows)
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


def no_suf(str, separator=bbcfg.ignore_sep):
    """Returns string before separator
    Ignores unique-identifier suffixes, e.g. so substance name can be
    used for molmassratio calculations or in lookup tables.
    """
    return str.split(separator)[0]


# DATA FRAME CONSTRUCTORS
def make_df(data, sheet=None, sep='\t', index=0, metaprefix="meta",
            col_order=False, T=False, drop_zero=False, sort=False,
            lower_cols=True, fillna=True, str_index=False):
    """Creates a Pandas dataframe from various file types

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
          str_index (bool): Forces index values to strings

     Returns:
         The generated dataframe.
    """
    logger.debug(f"Attempting to make dataframe from {data} ({type(data)}), (excel sheet: {sheet}")

    if isinstance(data, pan.DataFrame):
        df = data
        if df.empty:
            return df
    # Needs to at least be "truthy"
    elif bool(data) is True:
        # Contains key-value data itself (turn it into pandas df)
        if isinstance(data, (dict, list)):
            df = pan.DataFrame(data)
        # Contains file path
        elif isinstance(data, (Path, str)):
            filepath = Path(data)
            # Excel workbook
            if filepath.suffix in ['.xls', '.xlsx']:
                df = pan.read_excel(filepath, sheet_name=sheet, index_col=index)
            # Comma-separated or equivalent (readable by pandas)
            elif filepath.suffix in ['.csv', '.tsv', '.txt', '.dat']:
                df = pan.read_csv(filepath, sep=',', index_col=index)
    else:
        return pan.DataFrame()

    if str_index is True:
        df.index = df.index.astype('str')

    if metaprefix is not None:
        if index is not None:
            df = df[~(df.index.str.startswith(metaprefix))]
        cols = [col for col in list(df) if not col.startswith(metaprefix)]
        logger.debug(f"if you get an error here, check that the unit name is correct and exists in the unit library")
        df = df[cols]

    if type(col_order) is list:
        df = df[col_order]

    df = df.apply(pan.to_numeric, errors='ignore')  # if it looks like a number, make it a number

    if T is True:
        df = df.T

    if drop_zero is True:
        df = df.fillna(0)
        df = df.loc[:, (df != 0).any(axis=0)]
        df = df[np.square(df.values).sum(axis=1) != 0]  # uses square so that negative numbers aren't an issue

    if sort is True:
        df.sort_index()

    if lower_cols is True:
        df.columns = [clean_str(c) for c in df.columns]

    if fillna is True:
        df = df.fillna(0)
        if df.isnull().values.any() is True:
            logger.warning(f"Remaining null values: {df.isnull}")

    logger.debug(f"DataFrame created with columns: {df.columns}")

    return df


def mass_energy_df(df, energy_strings=bbcfg.energy_flows, totals=True, aggregate_consumed=False,
                   units=bbcfg.units_default):
    """Reorders dataframe to seperate mass and energy flows

    Uses a list of prefix/suffixes to identify mass and energy flows
    and reorders a dataframe to seperate them, orders them alphabetically,
    and also optionally adds rows for mass totals and energy totals.

    Args:
        energy_strings (list): contains strings of prefix/suffix to substance
            names that indicate an energy flow
            (Defaults to bbcfg.energy_flows)
        totals (bool): Appends summation rows for mass and energy seperately.
            (Defaults to True)
        units (dict): dictionary with keys of "mass" and "energy", and
            values for what the units used for each of those are
    """
    logger.debug(f"seperating mass and energy flows using {energy_strings} as energy flow markers")

    df = make_df(df, drop_zero=True)

    cols = list(df)

    mass_df = pan.DataFrame(columns=cols)
    energy_df = pan.DataFrame(columns=cols)
    consumed_mass_df = pan.DataFrame(columns=cols)
    consumed_energy_df = pan.DataFrame(columns=cols)

    for i, row in df.iterrows():
        if i.startswith(bbcfg.consumed_indicator):
            consumed = True
        else:
            consumed = False
        clean_i = clean_str(i, str_to_cut=bbcfg.consumed_indicator)
        energy_flow = False

        for string in energy_strings:
            if clean_i.startswith(string) or clean_i.endswith(string):
                energy_flow = True
                break

        if energy_flow is True:
            if consumed is True and aggregate_consumed is True:
                consumed_energy_df = consumed_energy_df.append(row)
            else:
                energy_df = energy_df.append(row)

        else:
            if consumed is True and aggregate_consumed is True:
                consumed_mass_df = consumed_mass_df.append(row)
            else:
                mass_df = mass_df.append(row)

    if aggregate_consumed is True:
        if not consumed_mass_df.empty:
            mass_df = mass_df.append(consumed_mass_df.sum().rename(f'CONSUMED/EMBODIED/&c mass'))
        if not consumed_energy_df.empty:
            energy_df = energy_df.append(consumed_energy_df.sum().rename(f'CONSUMED/EMBODIED/&c energy'))

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
            mass_df = mass_df.append(mass_df.sum().rename(f'TOTAL MASS, in {units.mass}'))
        if not energy_df.empty:
            energy_df = energy_df.append(energy_df.sum().rename(f'TOTAL ENERGY, in {units.energy}'))
    combined_df = pan.concat([mass_df, energy_df], keys=['Mass', 'Energy'], names=['type', 'substance'])

    return combined_df


def metadata_df(user=bbcfg.user, about=about.about_blackblox, name="unknown", level="unknown",
                product="unknown", product_qty="unknown", scenario="unknown",
                energy_flows=bbcfg.energy_flows, units=bbcfg.units_default):
    """Generates a metadata dataframe for use in excel file output
    """
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
            "09": f"balanced on {product_qty} {units.energy if is_energy(product) else units.mass} of {product} using the variable values from the {scenario} scenario(s).",
            "10": f"Mass quantites are given in {units.mass} and energy quantities in {units.energy}",
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

def build_unit_library(ul_file=None, ul_sheet=None):
    # Default parameters need to be set at call time instead of import time

    # A bit of a hack, but the big logic here and in make_df assume ul_file to be a string, so we convert,
    # because we need to accept also pathlib.Path
    file = str(bbcfg.paths.unit_process_library_file if ul_file is None else ul_file)
    sheet = str(bbcfg.paths.unit_process_library_sheet if ul_sheet is None else ul_sheet)

    df_unit_library_partial = make_df(file, sheet)

    var_id_col = []
    var_file_col = []
    var_sheet_col = []

    calc_id_col = []
    calc_file_col = []
    calc_sheet_col = []

    dir_list = [f.path for f in os.scandir(file.parent) if f.is_dir()]
    dir_list.append(file.parent)

    for d in dir_list:
        data_dir = Path(d)

        dir_files = os.listdir(data_dir)
        var_files = []
        calc_files = []
        unused_files = []

        for file in dir_files:
            if file.startswith(bbcfg.paths.var_filename_prefix):
                var_files.append(file)
            elif file.startswith(bbcfg.paths.calc_filename_prefix):
                calc_files.append(file)
            else:
                unused_files.append(file)

        for file in var_files:
            filepath = data_dir / file

            if filepath.suffix in ['.xls', '.xlsx']:
                xls = pan.ExcelFile(filepath)

                for sheet in xls.sheet_names:
                    if sheet in var_id_col:
                        pass
                    else:
                        var_id_col.append(sheet)
                        var_sheet_col.append(sheet)
                        var_file_col.append(filepath)
            elif filepath.suffix in ['.csv', '.tsv', '.txt', '.dat']:
                if file.strip(bbcfg.paths.var_filename_prefix).split('.', 1)[0] in var_id_col:
                    pass
                else:
                    var_id_col.append(file.strip(bbcfg.paths.var_filename_prefix).split('.', 1)[0])
                    var_sheet_col.append(0)
                    var_file_col.append(filepath)
            else:
                print(f"{filepath.suffix} files not supported. Skipping {file}.")

        for file in calc_files:
            filepath = data_dir / file

            if filepath.suffix in ['.xls', '.xlsx']:
                xls = pan.ExcelFile(filepath)
                for sheet in xls.sheet_names:
                    if sheet in calc_id_col:
                        pass
                    else:
                        calc_id_col.append(sheet)
                        calc_sheet_col.append(sheet)
                        calc_file_col.append(filepath)
            elif filepath.suffix in ['.csv', '.tsv', '.txt', '.dat']:
                if file.strip(bbcfg.paths.calc_filename_prefix).split('.', 1)[0] in calc_id_col:
                    pass
                else:
                    calc_id_col.append(file.strip(bbcfg.paths.calc_filename_prefix).split('.', 1)[0])
                    calc_sheet_col.append(0)
                    calc_file_col.append(filepath)
            else:
                print(f"{filepath.suffix} files not supported. Skipping {file}.")

    var_df = pan.DataFrame({
        bbcfg.columns.unit_id: var_id_col,
        bbcfg.columns.var_filepath: var_file_col,
        bbcfg.columns.var_sheetname: var_sheet_col,
    })
    var_df = var_df.set_index(bbcfg.columns.unit_id)

    calc_df = pan.DataFrame({
        bbcfg.columns.unit_id: calc_id_col,
        bbcfg.columns.calc_filepath: calc_file_col,
        bbcfg.columns.calc_sheetname: calc_sheet_col,
    })
    calc_df = calc_df.set_index(bbcfg.columns.unit_id)

    file_data = pan.merge(var_df, calc_df, on=bbcfg.columns.unit_id, how="inner")

    unit_library_merged = pan.merge(df_unit_library_partial, file_data, on=bbcfg.columns.unit_id, how="inner")

    return unit_library_merged

# WRITERS TO FILES

def build_filedir(filedir: Path, subfolder=None, file_id_list=[], time=True) -> Path:
    """ Builds complicated file directory names.
    Used for allowing file to be output to unique directories.

    Args:
        filedir (Path): the basename file directory
        subfolder (str): optional subfolder(s)
            (Defaults to None.)
        file_id_list (list of str): list of strings to append to the directory
            name. 
            (Defaults to an empty list.)
        time (bool): Whether to include a date-time stamp in the file
            directory  name. 
            (Defaults to True.)

    Returns:
        The built file directory Path.
    """

    if subfolder is not None:
        filedir = filedir / subfolder

    parent = filedir.parent
    basename = filedir.name

    for file_id in file_id_list:
        if file_id:
            basename = f'{basename}_{file_id}'

    if time:
        basename = f'{basename}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

    return parent / basename


def write_to_xls(df_or_df_list, sheet_list=None, outdir=None,
                 filename='output', subdir=None):
    """Writes one or more data frames to a single excel workbook.

    Each data frame appears on its own worksheet. Automatically creates the
    specified output folder if it does not exist.

    args:
        df_or_df_list (dataframe or list): A single pandas dataframe or list
            of pandas dataframes.
        sheet_list (optional, list): List of sheetnames that will be used for
            the dataframe at the same index in df_or_df_list. 
            (Defaults to None.)
        filedir (optional, Path): desired file output directory.
        filename (optional, str): desired excel file name, without extension.
            (Defaults to 'output')
    """
    filedir = outdir if outdir else bbcfg.path_outdir

    if subdir:
        (filedir / subdir).mkdir(parents=True, exist_ok=True)
    else:
        filedir.mkdir(parents=True, exist_ok=True)

    filename = filename.replace('/', '')
    filename_ext = filename + '.xlsx'
    filepath = filedir / (subdir if subdir else '') / filename_ext
    logger.debug(f"attempting to create {filename} in {filedir}")

    empty_notice = {'00': "The supplied dataframe was empty.",
                    '01': "This could happen is all the supplied values were zero",
                    '02': 'and rows with all zeros were dropped when the data frame was created.'}
    empty_df = pan.DataFrame.from_dict(empty_notice, orient='index', columns=['Empty Dataframe'])

    if isinstance(df_or_df_list, pan.DataFrame):
        df_or_df_list.to_excel(filepath)

    else:
        with pan.ExcelWriter(filepath) as writer:  # pylint: disable=abstract-class-instantiated
            for i, df in enumerate(df_or_df_list):
                if sheet_list:
                    sheet = sheet_list[i]
                else:
                    sheet = i
                if len(sheet) > 30:
                    sheet=sheet[0:28]
                if df.empty:
                    empty_df.to_excel(writer, sheet)
                else:
                    df.to_excel(writer, sheet)
                logger.debug(f"writing {sheet} sheet to workbook")

    logger.debug(f"{filename_ext} successfully created in {filedir}")


def format_and_save_plot(filepath):
    plt.style.use('tableau-colorblind10')
    plt.grid(True)
    plt.savefig(f"{filepath}.png", format='png', dpi=300)
    plt.savefig(f"{filepath}.svg", format='svg')

def plot_scenario_bars(df_dict, flow, outdir, file_id="", unit_dict=bbcfg.units_default):
    """
    Compare single flow between multiple scenarios in a single factory. Each scenario is a bar.
    Either for inflow, outflow, net flow or aggregate flow.
    """
    pass

def plot_annual_flows(df_dict, flow, outdir, file_id="", units=bbcfg.units_default):
    """
    Generated a line plot for each column of a dataframe, using the index
    as the x-axis labels (which should be a list of years).
    """
    flow_series = []
    for df_name in df_dict:
        if 'cumulative' in df_name:
            pass
        else:
            df = df_dict[df_name].fillna(0)
            if str.lower(flow) in df:
                s = df.loc[:, str.lower(flow)]
                s = s.rename(df_name)
                flow_series.append(s)

    flow_df = pan.concat(flow_series, axis=1, sort=True)
    flow_df.index = flow_df.index.map(int)  # converts year strings to integers
    df_index = flow_df.index.tolist()

    ticks = len(df_index)
    tick_step = 1
    while ticks > 20:
        ticks = ticks / 2
        tick_step = tick_step * 2

    flow_df.plot(title=f"annual outflows of {flow}")

    flow_unit = units.energy if is_energy(flow) else units.mass
    plt.xticks(range(df_index[0], df_index[-1] + 1, tick_step), rotation=90)
    plt.ylabel(f"{flow_unit} {flow}")

    format_and_save_plot(f'{outdir}/{flow}{file_id}')
    plt.close()


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
    return (defaultdict(final) if levels < 2 else
            defaultdict(lambda: nested_dicts(levels - 1, final)))
