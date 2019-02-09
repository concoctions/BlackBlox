from io_functions import makeDF
from pathlib import Path

# output directory  
outdir = 'outputFiles/'

# global data file
globalData = 'excelData/globalData.xlsx'

# get list of unit processes
df_unit_library = makeDF(globalData, sheet='Unit Processes')

# specify unitListTSV column headers:
unit_name_col = 'name'
unit_product = 'product'
unit_product_io = 'productType'
var_filepath = 'varFile'
var_sheetname = 'varSheet'
calc_filepath = 'calcFile'
calc_sheetname = 'calcSheet'

# specify calculation file column headers:
known = 'KnownQty'
known_io = 'k_QtyFrom'
unknown = 'UnknownQty'
unknown_io = 'u_QtyTo'
calc_type = 'Calculation'
calc_var = 'Variable'
no_var = ['none', 'false', 'na', '-'] #values that indicate there is no applicalbe variable

# specify variables files 
default_scenario = "default"

# specify production chain files column headers
inflow_col = 'Inflow'
outflow_col = 'Outflow'
process_col = 'Process'

# specify factory files column headers
chain_name = 'ChainName'
chain_product = 'ChainType'
chain_product = 'ChainProduct'
chain_io = 'Product_IO'
chain_filepath = 'ChainFile'
chain_sheetname = 'ChainSheet'
main_chain = 'main'
aux_chain_sig = 'aux'
multiconnect_aux_chain_sig = 'multi-aux'

origin_chain = "OriginChain"
origin_process = "OriginProcess"
dest_chain = "DestinationChain"
connect_product = "Product"
origin_io = "Product_IO_of_Origin"
dest_io = "Product_IO_of_Destination"
connect_all = 'all'

# Specify lookup variables (if seen in calc file, replaces with specific value from variable file)
lookup_var_dict = {
    'fuel': dict(data_frame=makeDF(globalData, sheet='Fuels'), lookup_var='fuelType')  #keyword string in calc file to trigger lookup: (dataframe of lookup data, column name in variable table to replace with) 
    }

# Specify shortcut names for lookup dataFrames:
df_fuels = lookup_var_dict['fuel']['data_frame']


