from io_functions import make_df
from pathlib import Path
from datetime import datetime

# DEFAULT FILEPATHS 
outdir = 'outputFiles' # default output directory 
globalData =  'excelData/globalData.xlsx'  # global data file, if one exists
unit_process_library_file = globalData
unit_process_library_sheet = 'Unit Processes'

# COLUMN HEADERS
# unit library table:
unit_name_col = 'name'
unit_product = 'product'
unit_product_io = 'productType'
var_filepath = 'varFile'
var_sheetname = 'varSheet'
calc_filepath = 'calcFile'
calc_sheetname = 'calcSheet'

# unit process calculations tables:
known = 'KnownQty'
known_io = 'k_QtyFrom'
unknown = 'UnknownQty'
unknown_io = 'u_QtyTo'
calc_type = 'Calculation'
calc_var = 'Variable'


# production chain tables:
inflow_col = 'Inflow'
outflow_col = 'Outflow'
process_col = 'Process'

# factory chain tables:
chain_name = 'ChainName'
chain_product = 'ChainType'
chain_product = 'ChainProduct'
chain_io = 'Product_IO'
chain_filepath = 'ChainFile'
chain_sheetname = 'ChainSheet'

# factory connections tables:
origin_chain = "OriginChain"
origin_process = "OriginProcess"
dest_chain = "DestinationChain"
connect_product = "Product"
origin_io = "Product_IO_of_Origin"
dest_io = "Product_IO_of_Destination"

# industry tables
factory_name = "Factory Name"
factory_filepath = "Factory File"
f_chain_list_file = "Chains File"
f_chains_sheet = "Factory Chains Sheet"
f_connections_file = "Connections File"
f_connections_sheet = "Factory Connections Sheet"

f_product = "Factory Product"
f_product_qty = "Product Qty"
f_scenario = "Scenario"


# SPECIAL FILE VARIALBES
default_scenario = "default" # in unit process variable table
connect_all = 'all' # in factory connections table (for origin_process only)
all_factories = ['industry', 'all', 'factories']
no_var = ['none', 'false', 'na', '-', '', 'nan'] # no variable marker for unit process calculations table
same_xls = ['thisfile', 'same', 'here'] # data in same workbook

# lookup variables for unit processcalculations table (replaces variable with specific value from variable file)
# lookup_var is the keyword string in calc file to trigger lookup: (dataframe of lookup data, column name in variable table to replace with) 
lookup_var_dict = { 
    'fuel': dict(data_frame=make_df(globalData, sheet='Fuels'), 
                 lookup_var='fuelType'),
    } 


# OTHER SHORTCUT NAMES
df_fuels = lookup_var_dict['fuel']['data_frame']
