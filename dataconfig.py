from io_functions import makeDF
from pathlib import Path


# get list of unit processes
df_unit_processes = makeDF(Path('globalData/unitList.tsv'))

# specify unitListTSV column headers:
unit_name_col = 'name'
default_product_col = 'product'
default_product_io_col = 'productType'
variables_filepath_col = 'varFile'
calculations_filepath_col = 'calcFile'

# specify calculation file column headers:
known_substance_col = 'KnownQty'
known_io_col = 'k_QtyFrom'
unknown_substance_col = 'UnknownQty'
unknown_io_col = 'u_QtyTo'
calculation_type_col = 'Calculation'
variable_col = 'Variable'
variables_to_ignore = ['none', 'false', 'na', '-'] #values that indicate there is no applicalbe variable

# specify variables files 

default_scenario = "default"


# specify production chain files column headers
inflow_col = 'Inflow'
outflow_col = 'Outflow'
process_col = 'Process'


# Specify lookup variables (if seen in calc file, replaces with specific value from variable file)
lookup_variables_dict = {
    'fuel': dict(data_frame=makeDF(Path('globalData/fuels.tsv')), lookup_var='fuelType')  #keyword string in calc file to trigger lookup: (dataframe of lookup data, column name in variable table to replace with) 
    }

# Specify shortcut names for lookup dataFrames:
df_fuels = lookup_variables_dict['fuel']['data_frame']


