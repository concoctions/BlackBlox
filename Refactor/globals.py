# LOCATE FILES
# see README.txt for specified file foramts
fuelsTSV = 'fuels.tsv'              # fuel combustion data
unitListTSV = 'unitList.tsv'        # list of unit processes


# File Settings
calcDir = ''                        # location of unit process calculation files
calc_index = None                   # column, if any, to be used as index

varDir = ''                         # location of of unit process variables files
var_index = 0                       # column, if any, to be used as index (e.g. scenarios)

sep = '\t'                      # file seperator (default: '\t' = tab)
metaPrefix = 'meta'
 


# standard functs
def makeDF(filePath, sep=sep, index=0, header='infer', metaprefix = metaPrefix, T = False):
    df = pan.read_csv(filePath, sep=sep, header=header, index_col=index, usecols = lambda x: not str(x).startswith(metaprefix))
    df = df_unitList[~df_unitList.index.str.startswith(metaprefix)]   

    if T = True:
        df = df.T

    return df

# initalize global variables
df_fuels = makeDF(fuelsTSV)
print df_fuels

df_unitList = makeDF(unitListTSV)
print df_unitList