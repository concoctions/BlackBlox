# -*- coding: utf-8 -*-
""" Data Input and Output default strings

This module contains variables used for default file paths, column headers
for input data files, as well as special variable strings (generally used)
to indicate whether something is All or None.

Please note that as of this time, non-column header variables are case and 
white space sensitive. All colum-header variables should be given in all 
lower case, to allow the input to be non case-sensitive

Module Outline:

- import statements and logger
- module variables: user data (dict)
- module variables: float_tol (int)
- module variables: default filepaths (str)
- module variables: lookup variables (dict)
- module variables: substance name variables
- module variables: column headers (str)
    - for unit process library tabular data
    - for unit process relationships tabular data
    - for product chain linkages tabular data
    - for factory product chain list tabular data
    - for factory linkages tabular data
    - for industry data

"""
from blackblox.bb_log import get_logger
from datetime import datetime


logger = get_logger("config")


# USER DATA
user_data = {
    "name": "Mysterious Stranger",
    "affiliation": "Mysterious Organization",
    "project": "Mysterious Project",
}

# FlOAT TOLERANCE
float_tol = 5
"""The number of decimal places after which (floating point) differences should be ignored.
If a number is calculated to be less than zero, it will be rounded to the number of decimal places
in the float tolerance. An error will only be raised if it is stil less than zero.
"""


# DEFAULT FILEPATHS 
unit_process_library_file = "data/unitlibrary.xlsx" 
"""str: The filepath whre the unit process library file exists.
"""

unit_process_library_sheet = "Unit Processes"
"""The worksheet of the unit process library, if in an Excel workbook

If not an excel worksheet, this variable should be None.
"""
day = datetime.now().strftime("%b%d") 
time = datetime.now().strftime("%H%M")   

outdir = 'output'+'/'+day
"""str: The file output directory.

Unless an absolute path is specified, BlackBlox will create the directory 
as a subfolder of the current working directory.
"""  

same_xls = ['thisfile', 'same', 'here']
"""list: strings indicating the data is in the current Excel workbook

Usable as a replacement for a filepath for input data that is in an
Excel workbook with multiple sheets. The correct Excel sheet must still
be specified.
"""


# LOOKUP VARIABLES
fuel_dict = dict(
    filepath='data/shared/fuels.xlsx',
    sheet='Fuels',
    lookup_var='fueltype'
)

lookup_var_dict = { 
    # FUELS
    'fuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='fueltype'),
    'other fuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='other fuel type'),
    'primary fuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='primary fuel type'),
    'secondary fuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='secondary fuel type'),
    'fossil fuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='fossil fuel type'),
    'biofuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='biofuel type'),
    'secondary biofuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='secondary biofuel type'),
    'reducing agent': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='reducing agent'),
    'waste fuel': dict(
        filepath='data/shared/fuels.xlsx',
        sheet='Fuels',
        is_fuel=True,
        lookup_var='waste fuel type'),

    # UPSTREAM
    'upstream outflows': dict(
        lookup_var='upstream outflows',
        filepath='data/shared/upstream.xlsx',
        sheet='up-emissions'),
    'upstream inflows': dict(
        lookup_var='upstream inflows',
        filepath='data/shared/upstream.xlsx',
        sheet='up-removals'),

    # DOWNSTREAM
    'downstream outflows': dict(
        lookup_var='downstream outflows',
        filepath='data/shared/upstream.xlsx',
        sheet='down-emissions'),
    'downstream inflows': dict(
        lookup_var='downstream inflows',
        filepath='data/shared/upstream.xlsx',
        sheet='down-removals'),

    # NO FURTHER DATA (only used to pass flowname from var_df)
    'biomass': dict(lookup_var='biomass type'),
    'feedstock': dict(lookup_var='feedstock type'),
    'fossil feedstock': dict(lookup_var='fossil feedstock type'),
    'biofeedstock': dict(lookup_var='biofeedstock type'),
    'alloy': dict(lookup_var='alloy type'),
    'solvent': dict(lookup_var='solvent type')
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

fuel_flows = ['fuel', 'other fuel', 'primary fuel', 'secondary fuel', 'fossil fuel', 'biofuel']
"""list: strings that indicate that a substance is an fuel flow

Usable in flow names. Must be used at the beginning or end of the flow name.
"""

# SUBSTANCE NAME VARIABLES
default_units = {
    'mass': 'tonnes',
    'energy': 'GJ',
}

energy_flows = ['heat', 'energy', 'electricity', 'power', 'LHV', 'HHV', 'lhv', 'hhv']
"""list: strings that, at the start or end of a flow identifier indicate an energy flow
"""

default_emissions = ['CO2__fossil', 'CO2__bio', 'H2O']
"""list: emissions that the program automatically checks for factors for.
"""

ignore_sep = '__'
"""str: indicator to ignore text after this string when performing calculations
This is useful when the calculation is sensitive to the substance name (e.g. in
MolMassRatio calculations or Combustion calculations), but when the substance
name needs to be unique (e.g. fuel__from place A, fuel__from place B)
"""

consumed_indicator = 'CONSUMED'
"""str: when this string begins a substance name (case sensitive), the substance
is ignored in the unit process inflows/outflows list and in the diagram. However,
it will still show up in the mass/energy balance.
E.g. 1 heat is used by a process and there is no useful heat byproduct, but
you still want it to show up in the energy balance.
E.g. 2. Process X produces product X which is used by Process Y, but it's not 
necessary to fully model process X; therefore in Process Y, product X is listed
as "CONSUMED" to indicate that it is factory-internal flow.
"""

# OTHER DATA NAMING VARIABLES
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
destination chain by the specified product, and therefore uses chain total
numbers to balance the destination chain.
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


# DIAGRAM LINE STYLING 
mass_color = 'black'
mass_style = 'solid'

energy_color = 'darkorange'
energy_style = 'dashed'

recycled_color = 'blue'

# COLUMN HEADERS:
# These should all be lower case here. In the file itself, case does not matter (though spaces do)

# for UNIT LIBRARY tabular data:
unit_id = 'id'
unit_name = 'display name'
unit_product = 'product'
unit_product_io = 'producttype'
var_filepath = 'varfile'
var_sheetname = 'varsheet'
calc_filepath = 'calcfile'
calc_sheetname = 'calcsheet'

# for UNIT PROCESS relationship tabular data:
known = 'knownqty'
known_io = 'k_qtyfrom'
unknown = 'unknownqty'
unknown_io = 'u_qtyto'
calc_type = 'calculation'
calc_var = 'variable'
known2 = '2nd known substance'
known2_io = '2qty origin'

# for UNIT PROCESS scenario values tabular data:
combustion_efficiency_var = 'combustion eff'

# for production CHAIN linkages tabular data:
inflow_col = 'inflow'
outflow_col = 'outflow'
process_col = 'process_id'

# for FACTORY chain list tabular data:
chain_name = 'chainname'
chain_product = 'chainproduct'
chain_io = 'product_io'
chain_filepath = 'chainfile'
chain_sheetname = 'chainsheet'
single_unit_chain = 'this unit only'

# for FACTORY connections tabular data:
origin_chain = "o chain"
origin_unit = "o unit"
origin_io = "o flowtype"
origin_product = "o product"
dest_chain = "d chain"
dest_unit = "d unit"
dest_product = "d product"
dest_io = "d flowtype"
replace = "r replacing"
purge_fraction = "r purge %"
max_replace_fraction = "r max replace %"

# for INDUSTRY tablular data
factory_name = "factory name"
factory_filepath = "factory file"
f_chain_list_file = "chains file"
f_chains_sheet = "factory chains sheet"
f_connections_file = "connections file"
f_connections_sheet = "factory connections sheet"
f_product = "factory product"
f_product_qty = "product qty"
f_scenario = "scenario"


# Other Filepaths
graphviz_path = 'C:/ProgramData/Anaconda3/Library/bin/graphviz/'
