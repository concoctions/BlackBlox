# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class UserConfig:
    name: str
    affiliation: str
    project: str


@dataclass
class UnitsDefaultConfig:
    mass: str
    energy: str


@dataclass
class DiagramConfig:
    """Diagram line styling"""
    mass_color: str
    mass_style: str
    energy_color: str
    energy_style: str
    recycled_color: str


@dataclass
class ColumnConfig:
    """Column headers

    These should all be lower case here. In the file itself, case does not matter (though spaces do)
    """

    # for UNIT LIBRARY tabular data:
    unit_id: str
    unit_name: str
    unit_product: str
    unit_product_io: str
    var_sheetname: str
    calc_sheetname: str
    var_filepath: str
    calc_filepath: str

    # for UNIT PROCESS relationship tabular data:
    known: str
    known_io: str
    unknown: str
    unknown_io: str
    calc_type: str
    calc_var: str
    known2: str
    known2_io: str

    # for UNIT PROCESS scenario values tabular data:
    combustion_efficiency_var: str

    # for production CHAIN linkages tabular data:
    inflow_col: str
    outflow_col: str
    process_col: str

    # for FACTORY chain list tabular data:
    chain_name: str
    chain_product: str
    chain_io: str
    chain_filepath: str
    chain_sheetname: str
    single_unit_chain: str

    # for FACTORY connections tabular data:
    origin_chain: str
    origin_unit: str
    origin_io: str
    origin_product: str
    dest_chain: str
    dest_unit: str
    dest_product: str
    dest_io: str
    replace: str
    purge_fraction: str
    max_replace_fraction: str

    # for INDUSTRY tabular data
    factory_name: str
    factory_filepath: str
    f_chain_list_file: str
    f_chains_sheet: str
    f_connections_file: str
    f_connections_sheet: str
    f_product: str
    f_product_qty: str
    f_scenario: str


@dataclass
class PathConfig:
    unit_process_library_sheet: str
    """The worksheet of the unit process library, if in an Excel workbook

    If not an excel worksheet, this variable should be None.
    """

    same_xls: List[str]
    """list: strings indicating the data is in the current Excel workbook

    Usable as a replacement for a filepath for input data that is in an
    Excel workbook with multiple sheets. The correct Excel sheet must still
    be specified.
    """

    unit_process_library_file: Path
    """str: The filepath whre the unit process library file exists."""

    var_filename_prefix: str
    calc_filename_prefix: str

    path_outdir: Path
    """str: The file output directory.

    Unless an absolute path is specified, BlackBlox will create the directory 
    as a subfolder of the current working directory.
    """

    @staticmethod
    def convention_paths_scenario_root(
            scenario: Path,
            unit_process_library_sheet: str,
            var_filename_prefix: str,
            calc_filename_prefix: str,
            same_xls: List[str],
            unit_process_library_file_suffix: Path,
            path_outdir_suffix: Path,
    ):
        data_subdirname_default = 'data'
        output_subdirname_default = 'output'
        return PathConfig(
            unit_process_library_sheet=unit_process_library_sheet,
            var_filename_prefix=var_filename_prefix,
            calc_filename_prefix=calc_filename_prefix,
            same_xls=same_xls,
            unit_process_library_file=scenario / data_subdirname_default / unit_process_library_file_suffix,
            path_outdir=scenario / output_subdirname_default / path_outdir_suffix,
        )


@dataclass
class SharedVarConfig:
    path_shared_fuels: Optional[Path]
    path_shared_upstream: Optional[Path]
    fuel_dict: dict

    lookup_var_dict: dict
    """dictionary of special lookup substance names
    lookup_var is a dictionary with the names of substance, that when used
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

    @staticmethod
    def convention_sharedvar_scenario_root(
        path_shared_fuels: Optional[Path],
        path_shared_upstream: Optional[Path],
    ):
        common_fuel_info_default = dict(
            filepath=path_shared_fuels,
            sheet=None,
            is_fuel=True,
        )

        lookup_var = {
            'fuel': common_fuel_info_default | dict(lookup_var='fueltype'),
            'other fuel': common_fuel_info_default | dict(lookup_var='other fuel type'),
            'primary fuel': common_fuel_info_default | dict(lookup_var='primary fuel type'),
            'secondary fuel': common_fuel_info_default | dict(lookup_var='secondary fuel type'),
            'fossil fuel': common_fuel_info_default | dict(lookup_var='fossil fuel type'),
            'biofuel': common_fuel_info_default | dict(lookup_var='biofuel type'),
            'secondary biofuel': common_fuel_info_default | dict(lookup_var='secondary biofuel type'),
            'reducing agent': common_fuel_info_default | dict(lookup_var='reducing agent'),
            'waste fuel': common_fuel_info_default | dict(lookup_var='waste fuel type'),

            'upstream outflows': dict(
                filepath=path_shared_upstream,
                sheet='up-emissions',
                lookup_var='upstream outflows',
            ),
            'upstream inflows': dict(
                filepath=path_shared_upstream,
                sheet='up-removals',
                lookup_var='upstream inflows',
            ),

            'downstream outflows': dict(
                filepath=path_shared_upstream,
                sheet='down-emissions',
                lookup_var='downstream outflows',
            ),
            'downstream inflows': dict(
                filepath=path_shared_upstream,
                sheet='down-removals',
                lookup_var='downstream inflows',
            ),

            'biomass': dict(lookup_var='biomass type'),
            'feedstock': dict(lookup_var='feedstock type'),
            'fossil feedstock': dict(lookup_var='fossil feedstock type'),
            'biofeedstock': dict(lookup_var='biofeedstock type'),
            'alloy': dict(lookup_var='alloy type'),
            'solvent': dict(lookup_var='solvent type')
        }

        return SharedVarConfig(
            path_shared_fuels=path_shared_fuels,
            path_shared_upstream=path_shared_upstream,
            fuel_dict=dict(
                filepath=path_shared_fuels,
                sheet='Fuels',
                lookup_var='fueltype',
            ),
            lookup_var_dict=lookup_var,
        )


@dataclass
class Config:
    user: UserConfig

    float_tol: int
    """
    Float tolerance

    The number of decimal places after which (floating point) differences should be ignored.
    If a number is calculated to be less than zero, it will be rounded to the number of decimal places
    in the float tolerance. An error will only be raised if it is stil less than zero.
    """

    fuel_flows: List[str]
    """list: strings that indicate that a substance is an fuel flow

    Usable in flow names. Must be used at the beginning or end of the flow name.
    """

    units_default: UnitsDefaultConfig

    energy_flows: List[str]
    """list: strings that, at the start or end of a flow identifier indicate an energy flow"""

    emissions: List[str]
    """list: emissions that the program automatically checks for factors for."""

    ignore_sep: str
    """str: indicator to ignore text after this string when performing calculations
    This is useful when the calculation is sensitive to the substance name (e.g. in
    MolMassRatio calculations or Combustion calculations), but when the substance
    name needs to be unique (e.g. fuel__from place A, fuel__from place B)
    """

    consumed_indicator: str
    """str: when this string begins a substance name (case sensitive), the substance
    is ignored in the unit process inflows/outflows list and in the diagram. However,
    it will still show up in the mass/energy balance.
    E.g. 1 heat is used by a process and there is no useful heat byproduct, but
    you still want it to show up in the energy balance.
    E.g. 2. Process X produces product X which is used by Process Y, but it's not 
    necessary to fully model process X; therefore in Process Y, product X is listed
    as "CONSUMED" to indicate that it is factory-internal flow.
    """

    scenario_default: str
    """str: the index used for the default scenario of variables

    Usable in the unit process variables data tables. 
    If present in the variables data index, the default scenario will be used
    when a scenario of variables is not otherwise specified.
    """

    no_var: List[str]
    """str: indicator that no variable is used in the calculation

    Usable in the unit process calculation table, to indicate that the 
    calculation type requires no variable beyond the names of the substances. 
    (e.g. MolMassRatio)
    """

    connect_all: str
    """str: indicator that all processes of a chain connect to the destination

    Usable in the factory connections table, for the "origin process" column.
    Indicates that  every process of the origin chain is connected to the 
    destination chain by the specified product, and therefore uses chain total
    numbers to balance the destination chain.
    """

    all_factories: List[str]
    """list: strings indicating all factories in a given industry

    Useable as a row index in industry scenario tables to indicate that a
    production quantity or scenario applies to all factories producing the 
    specified product. 

    If used to specify an industry-wide total product production quantity, 
    each factory producing that product should specify their production quantity 
    as a fraction of that total as a decimal between 0 and 1.
    """

    timestamp_str: str
    """str: Timestamp used mainly as prefix for output directories and files, thus disambuigating multiple runs"""

    diagram: DiagramConfig
    columns: ColumnConfig
    paths: PathConfig
    shared_var: SharedVarConfig
    graphviz_path: Path
