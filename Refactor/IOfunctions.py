import pandas as pan


def makeDF(filePath, sep='\t', index=0, header='infer', metaprefix = "meta", T = False):
    # import with specified settings, ignoring columns that start with specified meta prefix
    df = pan.read_csv(filePath, sep=sep, header=header, index_col=index, usecols = lambda x: not str(x).startswith(metaprefix))

    # drop meta
    df = df[~df.index.str.startswith(metaprefix)]   

    if T == True:
        df = df.T

    return df
