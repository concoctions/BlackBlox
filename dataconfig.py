# -*- coding: utf-8 -*-
""" Data Input and Output default strings

This module contains variables used for default file paths, column headers
for input data files, as well as special variable strings (generally used)
to indicate whether something is All or None.

Please note that as of this time, these variables are case and white space
sensitive.

"""

# DEFAULT FILEPATHS 
unit_process_library_file = 'excelData/globalData.xlsx' 
unit_process_library_sheet = 'Unit Processes' # if an excel worksheet, otherwise None
lookup_var_file = 'excelData/globalData.xlsx' # if an excel workbook, otherwise specify in custom_lookup
outdir = 'BlackBlox_output' 


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

# industry data tables
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
same_xls = ['thisfile', 'same', 'here'] # for input filepaths; used to indicate that the data is in the same file

default_scenario = "default" # row index in unit process variable table
no_var = ['none', 'false', 'na', '-', '', 'nan'] # no variable marker for unit process calculations table

connect_all = 'all' # in factory connections table (for origin_process only)

all_factories = ['industry', 'all', 'factories'] # to indicate all factories in a given industry



