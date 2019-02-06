import pandas as pan


def makeDF(filePath, sep='\t', index=0, header='infer', metaprefix = "meta", T = False):
    # import with specified settings, ignoring columns that start with specified meta prefix
    df = pan.read_csv(filePath, sep=sep, header=header, index_col=index, usecols = lambda x: not str(x).startswith(metaprefix))

    # drop meta
    if index != None:
        df = df[~df.index.str.startswith(metaprefix)]   
    if T == True:
        df = df.T

    #if it looks like a number, make it a number:
    df = df.apply(pan.to_numeric, errors = 'ignore')

    return df


def check_if_df(data, index=0):
        if isinstance(data, pan.DataFrame):
            return data

        else:
            return makeDF(data, index=index)

# def write_df_to_excel(df_list)
    # """
    # using xlsxwriter
    # """
#     if isinstance(df_list, pan.DataFrame):
#         df_list = [df_list]
