from datetime import datetime
from pathlib import Path
from typing import List, Dict

import pandas
import yaml

from dataconfig_defaults import default as defcfgs
from dataconfig_format import Config, PathConfig
from io_functions import build_unit_library
from factory import Factory
from processchain import ProductChain
from unitprocess import UnitProcess


def run_scenario_file(filename: Path):
    with open(filename, 'r') as f:
        scenario_dict = yaml.load(f, Loader=yaml.FullLoader)
        validated_dict = __validate_scenario_dict(scenario_dict)

        __run_validated_dict(validated_dict)


def __build_unit_libraries(unit_library_dicts) -> Dict[str, pandas.DataFrame]:
    built_unit_libraries = {}

    for ul_dict in unit_library_dicts:
        ul_id = ul_dict['id']
        ul_params = ul_dict['params']

        built_filename = ul_params.get('file', None)
        built_filepath = Path(built_filename) if built_filename is not None else None
        built_sheet = ul_params.get('sheet', None)

        built_library = build_unit_library(ul_file=built_filepath, ul_sheet=built_sheet)
        built_unit_libraries[ul_id] = built_library

    return built_unit_libraries


def __build_unit_processes(unit_process_dicts, unit_libraries) -> Dict[str, UnitProcess]:
    built_unit_processes = {}

    for up_dict in unit_process_dicts:
        up_id = up_dict['id']
        up_params = up_dict['params']

        built_unit_library_id = up_params.get('unit_library_id', None)
        built_unit_library = unit_libraries[built_unit_library_id] if built_unit_library_id is not None else None
        built_outdir = up_params.get('outdir', None)

        built_process = UnitProcess(u_id=up_id, outdir=built_outdir, units_df=built_unit_library)
        built_unit_processes[up_id] = built_process

    return built_unit_processes


def __build_product_chains(product_chain_dicts) -> Dict[str, ProductChain]:
    pass


def __build_factories(factory_dicts) -> Dict[str, Factory]:
    pass


def __build_bbcfgs_with_defaults(cfgs: dict) -> Config:
    # for bbcfg basically everything is optional
    # thus we just start with the default cfg, and override ONLY what is specififed in the YAML
    built_cfg = defcfgs

    if 'user' in cfgs.keys():
        cfgs_user = cfgs['user']

        built_name = cfgs_user.get('name', None)
        if built_name is not None:
            built_cfg.user.name = built_name

        built_affiliation = cfgs_user.get('affiliation', None)
        if built_affiliation is not None:
            built_cfg.user.affiliation = built_affiliation

        built_project = cfgs_user.get('project', None)
        if built_project is not None:
            built_cfg.user.project = built_project

    if 'units_default' in cfgs.keys():
        cfgs_units_default = cfgs['units_default']

        built_mass = cfgs_units_default.get('mass', None)
        if built_mass is not None:
            built_cfg.units_default.mass = built_mass

        built_energy = cfgs_units_default.get('energy', None)
        if built_energy is not None:
            built_cfg.units_default.energy = built_energy

    built_emissions = cfgs.get('emissions', defcfgs.default.emissions)
    built_cfg.emissions = built_emissions

    built_scenario_default = cfgs.get('scenario_default', defcfgs.scenario_default)
    built_cfg.scenario_default = built_scenario_default

    # If paths_convention is present, build according to convention, otherwise the defaults from the source code
    built_cfg.paths = defcfgs.paths

    if 'paths_convention' in cfgs.keys():
        cfgs_paths = cfgs['paths_convention']

        # default is CWD
        cfg_scenario_root = cfgs_paths.get('scenario_root', None)
        built_scenario_root = Path() if cfg_scenario_root is None else Path(cfgs_paths['scenario_root'])

        cfg_UP_sheet = cfgs_paths.get('unit_process_library_sheet', None)
        built_UP_sheet = defcfgs.paths.unit_process_library_sheet if cfg_UP_sheet is None else cfg_UP_sheet

        cfg_var_filename_prefix = cfgs_paths('var_filename_prefix', None)
        built_var_filename_prefix = defcfgs.paths.var_filename_prefix if cfg_var_filename_prefix is None else cfg_var_filename_prefix

        cfg_calc_filename_prefix = cfgs_paths('cfg_calc_filename_prefix', None)
        built_calc_filename_prefix = defcfgs.paths.calc_filename_prefix if cfg_calc_filename_prefix is None else cfg_calc_filename_prefix

        cfg_same_xls = cfgs_paths('same_xls', None)
        built_same_xls = defcfgs.paths.same_xls if cfg_same_xls is None else cfg_same_xls

        cfg_path_outdir_suffix = cfgs_paths('path_outdir_suffix', None)
        built_path_outdir_suffix = datetime.now().strftime("%Y%m%dT%H%M") if cfg_path_outdir_suffix is None else cfg_path_outdir_suffix

        cfg_UP_filesuffix = cfgs_paths('unit_process_library_file_suffix', None)
        built_UP_filesuffix = Path('unitlibrary.csv') if cfg_UP_filesuffix is None else cfg_UP_filesuffix

        built_cfg.paths = PathConfig.convention_paths_scenario_root(
            scenario=built_scenario_root,
            unit_process_library_sheet=built_UP_sheet,
            var_filename_prefix=built_var_filename_prefix,
            calc_filename_prefix=built_calc_filename_prefix,
            same_xls=built_same_xls,
            unit_process_library_file_suffix=built_UP_filesuffix,
            path_outdir_suffix=built_path_outdir_suffix,
        )

    return built_cfg


def __validate_scenario_dict(scenario_dict: dict):
    # cfgs is a dictionary, all the rest are lists
    cfgs_dict = scenario_dict.get('bbcfg', {})
    unit_library_dicts = scenario_dict.get('unit_libraries', [])
    unit_process_dicts = scenario_dict.get('unit_processes', [])
    product_chain_dicts = scenario_dict.get('product_chains', [])
    factory_dicts = scenario_dict.get('factories', [])
    command_dicts = scenario_dict.get('commands', [])

    error_list = []
    validated_commands = []

    # Check that all commands refer only to ids of actually existing entities
    for c in command_dicts:
        for k in c.keys():  # each command is a dictionary with single key (the command name) and single value (props)
            elem_id = c[k]['id']
            if k == 'unit_process_balance' or k == 'unit_process_run_scenarios':
                if elem_id in [up['id'] for up in unit_process_dicts]:
                    validated_commands += [{k: c[k]}]
                else:
                    error_list += [f"WARNING: Unit process '{elem_id}' mentioned in commands but not declared."]
            elif k == 'product_chain_balance' or k == 'product_chain_run_scenarios':
                if elem_id in [pc['id'] for pc in product_chain_dicts]:
                    validated_commands += [{k: c[k]}]
                else:
                    error_list += [f"WARNING: Product chain '{elem_id}' mentioned in commands but not declared."]
            elif k == 'factory_balance':
                if elem_id in [f['id'] for f in factory_dicts]:
                    validated_commands += [{k: c[k]}]
                else:
                    error_list += [f"WARNING: Factory '{elem_id}' mentioned in commands but not declared."]
            else:
                pass

    # All the sections EXCEPT commands may have defaults (omitted in the YAML) that we fill in
    built_cfgs = __build_bbcfgs_with_defaults(cfgs_dict)
    built_unit_libraries = __build_unit_libraries(unit_library_dicts)
    built_unit_processes = __build_unit_processes(unit_process_dicts, built_unit_libraries)
    built_product_chains = __build_product_chains(product_chain_dicts)
    built_factories = __build_factories(factory_dicts)

    # TODO: return all entities together? bundled in dict?
    # TODO: remove debug
    print(f"Validation errors: {error_list}")
    for c in validated_commands:
        print(c)

    return validated_commands


def __run_validated_dict(validated_dict: dict):
    pass
