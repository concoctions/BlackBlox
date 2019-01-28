from IOfunctions import makeDF

# see README.txt for specified file foramts

# File Settings
 
# get list of unit processes
unitListTSV = 'unitList.tsv'        # list of unit processes
df_unitList = makeDF(unitListTSV)
print(df_unitList)

# Specify lookup variables
lookupVar = {
    'fuel': makeDF('fuels.tsv')
    }

print(lookupVar['fuel'])




