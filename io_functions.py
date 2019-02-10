import pandas as pan
from pathlib import Path
from collections import defaultdict

def makeDF(filePath, sheet=None, sep='\t', index=0, metaprefix = "meta", T = False):
    """ Creates a dataframe from an excel file or tab or comma seperated text file.

    Args:
        filePath
        sheet
        sep
        index
        metaprefix
        T

    Returns:
        df: dataframe

    """
    # import with specified settings, ignoring columns that start with specified meta prefix

    if filePath.endswith(('.xls', 'xlsx')):
        df = pan.read_excel(filePath, sheet_name=sheet, index_col=index)

    elif filePath.endswith('.csv'):
        df = pan.read_csv(filePath, sep=',', index_col=index)

    else:
        df = pan.read_csv(filePath, sep=sep, index_col=index) 
                 
    #usecols = lambda x: not str(x).startswith(metaprefix))

    # drop meta
    if index != None:
        df = df[~df.index.str.startswith(metaprefix)]

    cols = [col for col in list(df) if not col.startswith(metaprefix)]
    df = df[cols]

    if T == True:
        df = df.T

    #if it looks like a number, make it a number:
    df = df.apply(pan.to_numeric, errors = 'ignore')

    return df


def check_if_df(data, sheet=None, index=0):
    """ Checks if data is already a dataframe or not and returns a dataframe
    This function is used to allow for dataframes to be passed between functions
    if they already exist, and if not, to create them.

    """
    if isinstance(data, pan.DataFrame):
       return data

    else:
        return makeDF(data, sheet=sheet, index=index)

def write_to_excel(df_or_df_list, sheet_list=None, filedir='outputFiles', filename='output'):
    """writes one or more dataframes to a single excel file

    args:
        df_or_df_list (dataframe or list): A single pandas dataframe or list
            of pandas dataframes.
        sheet_list (optional, list): List of sheetnames that will be used for
            the dataframe at the same index in df_or_df_list. 
            Defaults to None.
        filedir (optional, str): desired file output directory. 
            Defaults to current working directory.
        filename (optional, str): desired excel file name, without extension.
            Defaults to 'output'
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


def fl(string):
    """returns the first letter of a string after striping white space
    """
    string = string.strip()
    string = str.lower(string[0])

    return string

def s_l(string_to_check):
    """strips a string of white space and lowers any capitals
    """
    string = ''.join(string_to_check)

    string = string.strip()
    string = str.lower(string)

    return string

def if_str(string):
    """checks if an input is a string, returns string if so, None if not.
    """
    if type(string) is str:
        return string
    else:
        return None

def check_sheet(df, sheetcol, index):
    if sheetcol in df:
        if type(df.loc[index, sheetcol]) is str:
            return df.loc[index, sheetcol]

    return None


def nested_dicts(levels=2, final=float):
    """returns a nested defaultdict of the specified number of levels
    source: https://goo.gl/Wq5kLq
    """
    return (defaultdict(final) if levels <2 else
            defaultdict(lambda: nested_dicts(levels - 1, final)))