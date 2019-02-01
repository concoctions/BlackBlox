from IOfunctions import makeDF

# see README.txt for specified file foramts

# File Settings

 
# get list of unit processes
unitListTSV = 'unitList.tsv'        # list of unit processes
df_unitList = makeDF(unitListTSV)

# specify unitListTSV column headers:
ul_name = 'name'
ul_product = 'product'
ul_productIO = 'productType'
ul_varFileLoc = 'varFile'
ul_calcFileLoc = 'calcFile'

# specify calculation file column headers:
c_known = 'KnownQty'
c_kFrom = 'k_QtyFrom'
c_unknown = 'UnknownQty'
c_uTo = 'u_QtyTo'
c_calcType = 'Calculation'
c_var = 'Variable'
ignoreVar = ['none', 'false', 'na', '-'] #values that indicate there is no applicalbe variable

# specify flow files column headers
origin = 'From'
destination = 'To'


# Specify lookup variables (if seen in calc file, replaces with specific value from variable file)
lookupVar = {
    'fuel': (makeDF('fuels.tsv'), 'fuelType')  #keyword string in calc file to trigger lookup: (dataframe of lookup data, column name in variable table to replace with) 
    }

# Specify shortcut names for lookup dataFrames:
df_fuels = lookupVar['fuel'][0]




