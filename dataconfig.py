# -*- coding: utf-8 -*-
""" Data Input and Output default strings

This module contains variables used for default file paths, column headers
for input data files, as well as special variable strings (generally used)
to indicate whether something is All or None.

Please note that as of this time, these variables are case and white space
sensitive.

Module Outline:

- import statements and logger
- module variables: default filepaths (str)
- module variables: user data (dict)
- module variables: column headers (str)
    - for unit process library tabular data
    - for unit process relationships tabular data
    - for product chain linkages tabular data
    - for factory product chain list tabular data
    - for factory linkages tabular data
    - for industry data
- module variables: reserved words for tabular data
    - same_xls (list)
    - default_scenario (str)
    - no_var (list)
    - massless_flows (list)
    - connect_all (str)
    - all_factories (list)

"""

from bb_log import get_logger
logger = get_logger("config")



# DEFAULT FILEPATHS 
unit_process_library_file = "data/unitlibrary.xlsx" 
"""str: The filepath whre the unit process library file exists.
"""

unit_process_library_sheet = "Unit Processes"
"""The worksheet of the unit process library, if in an Excel workbook

If not an excel worksheet, this variable should be None.
"""

outdir = 'output/demo' 
"""str: The file output directory.

Unless an absolute path is specified, BlackBlox will create the directory 
as a subfolder of the current working directory.
"""        


# USER DATA
user_data = {"name": "Mysterious Stranger",
             "affiliation": "Mysterious Organization",
             "project": "Mysterious Project",
}


# LOOKUP VARIABLES
lookup_var_dict = { 
    'fuel': dict(filepath='data/fuels.xlsx',
                 sheet='Fuels',
                 lookup_var='fuelType'),
    'fossil fuel': dict(filepath='data/fuels.xlsx',
                 sheet='Fuels',
                 lookup_var='fossil fuel type'),
    'biofuel': dict(filepath='data/fuels.xlsx',
                 sheet='Fuels',
                 lookup_var='biofuel type'),
} 
"""dictionary of special lookup substance names
Lookup_var_dict is a dictionary with the names of substance, that when used
in the unit process calculations file, will trigger the program to replace
the lookup substance name with the substance name specified in the unit 
process's variable data table for the scenario currently in use.

Each entry in this dictionary should be formatted with the following:

    **key** *(str)*: the substance name to be used in the calcuations file

    **value** *(dict)*: a dictionary of lookup variable attributes, containing:
        **lookup_var** *(str)*: the header of the column in the unit process 
        variable file that contains the value with which to replace
        the lookup substance word.

        **data_frame** *(optional)*: a data frame with additional custom data
        about the lookup variable, such as to be used in custom functions,
        below. These are not used elsewhere in BlackBlox.py.

"""

# SUBSTANCE VARIABLES

default_units = {'mass': 'tonnes', 
                 'energy':'GJ',
}


energy_flows = ['heat', 'energy', 'electricity', 'power']
"""list: indicator that a substance is an energy flow

Usable in flow names. Must be used at the beginning or end of the flow name.
"""

default_emissions = ['CO2', 'SO2', 'H2O']

# COLUMN HEADERS
# for UNIT LIBRARY tabular data:
unit_id = 'ID'
unit_name = 'display name'
unit_product = 'product'
unit_product_io = 'productType'
var_filepath = 'varFile'
var_sheetname = 'varSheet'
calc_filepath = 'calcFile'
calc_sheetname = 'calcSheet'

# for UNIT PROCESS relationship tabular data:
known = 'KnownQty'
known_io = 'k_QtyFrom'
unknown = 'UnknownQty'
unknown_io = 'u_QtyTo'
calc_type = 'Calculation'
calc_var = 'Variable'
known2 = '2nd Known Substance'
known2_io = '2Qty Origin'

# for UNIT PROCESS scenario values tabular data:
combustion_efficiency_var = 'combustEff'

# for production CHAIN linkages tabular data:
inflow_col = 'Inflow'
outflow_col = 'Outflow'
process_col = 'Process_ID'

# for FACTORY chain list tabular data:
chain_name = 'ChainName'
chain_product = 'ChainType'
chain_product = 'ChainProduct'
chain_io = 'Product_IO'
chain_filepath = 'ChainFile'
chain_sheetname = 'ChainSheet'

# for FACTORY connections tabular data:
origin_chain = "Origin_Chain"
origin_unit = "Origin_Unit"
origin_io = "Product_IO_of_Origin"
connect_product = "Product"
dest_chain = "Destination_Chain"
dest_unit = "Destination_Unit"
dest_io = "Product_IO_of_Destination"
replace = "Recycle_Replacing"
purge_fraction = "Purge_Fraction"
max_replace_fraction = "Max_Replace_Fraction"


# for INDUSTRY tablular data
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
same_xls = ['thisfile', 'same', 'here']
"""list: strings indicating the data is in the current Excel workbook

Usable as a replacement for a filepath for input data that is in an
Excel workbook with multiple sheets. The correct Excel sheet must still
be specified.
"""

default_scenario = "default" 
"""str: the index used for the default scenario of variables

Usable in the unit process variables data tables. 
If present in the variables data index, the default scenario will be used
when a scenario of variables is not otherwise specified.
"""

no_var = ['None', 'none', 'false', 'na', '-', '--', '', 'nan', 0, '0', None, False, float('nan')] 
"""str: indicator that no variable is used in the calculation

Usable in the unit process calculation table, to indicate that the 
calculation type requires no variable beyond the names of the substances. 
(e.g. MolMassRatio)
"""

connect_all = 'all'
"""str: indicator that all processes of a chain connect to the destination

Usable in the factory connections table, for the "origin process" column.
Indicates that  every process of the origin chain is connected to the 
destination chain by the specified product.
"""

all_factories = ['industry', 'all', 'factories'] 
"""list: strings indicating all factories in a given industry

Useable as a row index in industry scenario tables to indicate that a
production quantity or scenario applies to all factories producing the 
specified product. 

If used to specify an industry-wide total product production quantity, 
each factory producing that product should specify their production quantity 
as a fraction of that total as a decimal between 0 and 1.
"""