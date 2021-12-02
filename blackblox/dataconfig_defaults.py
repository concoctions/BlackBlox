# -*- coding: utf-8 -*-
""" Data Input and Output default strings

This module contains variables used for default file paths, column headers
for input data files, as well as special variable strings (generally used)
to indicate whether something is All or None.

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
from pathlib import Path

from blackblox.dataconfig_format import UserConfig, UnitsDefaultConfig, DiagramConfig, ColumnConfig, PathConfig, SharedVarConfig, Config


user_default = UserConfig(
    name="Anonymous",
    affiliation="",
    project="",
)

float_tol_default = 5
fuel_flows_default = ['fuel', 'other fuel', 'primary fuel', 'secondary fuel', 'fossil fuel', 'biofuel']

# SUBSTANCE NAME VARIABLES
units_default_default = UnitsDefaultConfig(
    mass='tonnes',
    energy='GJ',
)

energy_flows_default = ['heat', 'energy', 'electricity', 'power', 'LHV', 'HHV', 'lhv', 'hhv']
emissions_default = ['CO2__fossil', 'CO2__bio', 'H2O', 'contrib_CO2__bio-annual', 'contrib_CO2__bio-long']
ignore_sep_default = '__'
consumed_indicator_default = 'CONSUMED'

# OTHER DATA NAMING VARIABLES
scenario_default_default = "BASE"  # "default" is used in older scripts

no_var_default = ['None', 'none', 'false', 'na', '-', '--', '', 'nan', 0, '0', None, False, float('nan')]
connect_all_default = 'all'
all_factories_default = ['industry', 'all', 'factories']


# ISO8601 basic format date/time standard representation as default. It's great
day_str_default = datetime.now().strftime("%Y%m%d")
time_str_default = datetime.now().strftime("%H%M")
timestamp_str_default = day_str_default + 'T' + time_str_default


# Diagram line styling
diagram_default = DiagramConfig(
    mass_color='black',
    mass_style='solid',
    energy_color='darkorange',
    energy_style='dashed',
    recycled_color='blue',
)


# COLUMN HEADERS:
# These should all be lower case here. In the file itself, case does not matter (though spaces do)
columns_default = ColumnConfig(
    # for UNIT LIBRARY tabular data:
    unit_id='id',
    unit_name='display name',
    unit_product='product',
    unit_product_io='producttype',
    var_sheetname='varsheet',
    calc_sheetname='calcsheet',
    var_filepath='varfile',  # this column stores a filepath relative to path_data_root
    calc_filepath='calcfile',  # this column stores a filepath relative to path_data_root

    # for UNIT PROCESS relationship tabular data:
    known='knownqty',
    known_io='k_qtyfrom',
    unknown='unknownqty',
    unknown_io='u_qtyto',
    calc_type='calculation',
    calc_var='variable',
    known2='2nd known substance',
    known2_io='2qty origin',

    # for UNIT PROCESS scenario values tabular data:
    combustion_efficiency_var='combustion eff',

    # for production CHAIN linkages tabular data:
    inflow_col='inflow',
    outflow_col='outflow',
    process_col='process_id',

    # for FACTORY chain list tabular data:
    chain_name='chainname',
    chain_product='chainproduct',
    chain_io='product_io',
    chain_filepath='chainfile',
    chain_sheetname='chainsheet',
    single_unit_chain='this unit only',

    # for FACTORY connections tabular data:
    origin_chain="o chain",
    origin_unit="o unit",
    origin_io="o flowtype",
    origin_product="o product",
    dest_chain="d chain",
    dest_unit="d unit",
    dest_product="d product",
    dest_io="d flowtype",
    replace="r replacing",
    purge_fraction="r purge %",
    max_replace_fraction="r max replace %",

    # for INDUSTRY tabular data
    factory_name="factory name",
    factory_filepath="factory file",
    f_chain_list_file="chains file",
    f_chains_sheet="factory chains sheet",
    f_connections_file="connections file",
    f_connections_sheet="factory connections sheet",
    f_product="factory product",
    f_product_qty="product qty",
    f_scenario="scenario",
)


# DEFAULT FILEPATHS
path_project_root_default = Path()  # current working directory
path_data_root_default = path_project_root_default / 'data'

paths_default = PathConfig(
    unit_process_library_file=path_data_root_default / 'unitlibrary.xlsx',
    unit_process_library_sheet="Unit Processes",
    path_outdir=path_project_root_default / 'output',
    same_xls=['thisfile', 'same', 'here'],
)


# LOOKUP VARIABLES
path_data_shared_default = path_data_root_default / 'shared'
path_shared_fuels_default = path_data_shared_default / 'fuels.xlsx'

common_fuel_info_default = dict(
    filepath=path_shared_fuels_default,
    sheet='Fuels',
    is_fuel=True,
)

lookup_var_default = {
    # FUELS
    'fuel': dict(common_fuel_info_default, lookup_var='fueltype'),
    'other fuel': dict(common_fuel_info_default, lookup_var='other fuel type'),
    'primary fuel': dict(common_fuel_info_default, lookup_var='primary fuel type'),
    'secondary fuel': dict(common_fuel_info_default, lookup_var='secondary fuel type'),
    'fossil fuel': dict(common_fuel_info_default, lookup_var='fossil fuel type'),
    'biofuel': dict(common_fuel_info_default, lookup_var='biofuel type'),
    'secondary biofuel': dict(common_fuel_info_default, lookup_var='secondary biofuel type'),
    'reducing agent': dict(common_fuel_info_default, lookup_var='reducing agent'),
    'waste fuel': dict(common_fuel_info_default, lookup_var='waste fuel type'),

    # UPSTREAM
    'upstream outflows': dict(
        filepath=path_shared_upstream_default,
        sheet='up-emissions',
        lookup_var='upstream outflows',
    ),
    'upstream inflows': dict(
        filepath=path_shared_upstream_default,
        sheet='up-removals',
        lookup_var='upstream inflows',
    ),

    # DOWNSTREAM
    'downstream outflows': dict(
        filepath=path_shared_upstream_default,
        sheet='down-emissions',
        lookup_var='downstream outflows',
    ),
    'downstream inflows': dict(
        filepath=path_shared_upstream_default,
        sheet='down-removals',
        lookup_var='downstream inflows',
    ),

    # NO FURTHER DATA (only used to pass flowname from var_df)
    'biomass': dict(lookup_var='biomass type'),
    'feedstock': dict(lookup_var='feedstock type'),
    'fossil feedstock': dict(lookup_var='fossil feedstock type'),
    'biofeedstock': dict(lookup_var='biofeedstock type'),
    'alloy': dict(lookup_var='alloy type'),
    'solvent': dict(lookup_var='solvent type')
}


shared_var_default = SharedVarConfig(
    path_shared_fuels=path_shared_fuels_default,
    path_shared_upstream=path_data_shared_default / 'upstream.xlsx',
    fuel_dict=dict(
        filepath=path_shared_fuels_default,
        sheet='Fuels',
        lookup_var='fueltype',
    ),
    lookup_var_dict=lookup_var_default,
)


graphviz_path_default = Path('C:/ProgramData/Anaconda3/Library/bin/graphviz/')


default = Config(
    user=user_default,
    float_tol=float_tol_default,
    fuel_flows=fuel_flows_default,
    units_default=units_default_default,
    energy_flows=energy_flows_default,
    emissions=emissions_default,
    ignore_sep=ignore_sep_default,
    consumed_indicator=consumed_indicator_default,
    scenario_default=scenario_default_default,
    no_var=no_var_default,
    connect_all=connect_all_default,
    all_factories=all_factories_default,
    timestamp_str=timestamp_str_default,
    diagram=diagram_default,
    columns=columns_default,
    paths=paths_default,
    shared_var=shared_var_default,
    graphviz_path=graphviz_path_default,
)
"""The default configuration object, values chosen based on what is needed to run the "demo" scenario."""
