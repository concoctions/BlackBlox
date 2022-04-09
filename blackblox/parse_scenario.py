from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from pprint import pformat
from textwrap import dedent

import pandas as pd
import yaml

from blackblox.dataconfig_defaults import default as defcfgs
from blackblox.dataconfig_format import Config, PathConfig, SharedVarConfig
import blackblox.dataconfig
from blackblox.io_functions import build_unit_library
from blackblox.factory import Factory
from blackblox.processchain import ProductChain
from blackblox.unitprocess import UnitProcess


def run_scenario_file(yaml_file_path: Path):
    print(dedent("""
        Running BlackBlox scenario
        ==========================

        Scenario configuration file (full path) = "{}"

    """.format(yaml_file_path.resolve())
    ))

    with open(yaml_file_path, 'r') as f:
        scenario_dict = yaml.load(f, Loader=yaml.FullLoader)
        config_file_dir = yaml_file_path.parent
        cfg, entities, commands = __validate_scenario_dict(config_file_dir, scenario_dict)

        __run_validated_dict(cfg, entities, commands)


def __build_unit_libraries(unit_library_dicts, scenario_root: Path) -> Dict[str, pd.DataFrame]:
    built_unit_libraries = {}

    for ul_dict in unit_library_dicts:
        ul_id = ul_dict['id']
        ul_params = ul_dict['params']

        built_filename = ul_params.get('file', None)
        # (ab)using short-circuit and duck-typing here, None is falseish and bool(y) == True implies that (x and y) == y
        # If not None, outdir should be relative to '<bbcfg.scenario_root>/data'
        built_filepath_rel = built_filename and (scenario_root / 'data' / Path(built_filename))

        built_sheet = ul_params.get('sheet', None)

        built_library = build_unit_library(ul_file=built_filepath_rel, ul_sheet=built_sheet)
        built_unit_libraries[ul_id] = built_library

    return built_unit_libraries


def __build_unit_processes(unit_process_dicts, unit_libraries, scenario_root: Path) -> Dict[str, UnitProcess]:
    built_unit_processes = {}

    for up_dict in unit_process_dicts:
        up_id = up_dict['id']
        up_params = up_dict['params']

        built_unit_library_id = up_params.get('unit_library_id', None)
        # (ab)using short-circuit and duck-typing here, None is falseish and bool(y) == True implies that (x and y) == y
        built_unit_library = built_unit_library_id and unit_libraries[built_unit_library_id]

        built_outdir = up_params.get('outdir', None)
        # If not None, outdir should be relative to '<bbcfg.scenario_root>'
        outdir_rel = built_outdir and (scenario_root / Path(built_outdir))

        built_process = UnitProcess(u_id=up_id, outdir=outdir_rel, units_df=built_unit_library)
        built_unit_processes[up_id] = built_process

    return built_unit_processes


def __build_product_chains(product_chain_dicts, unit_libraries, scenario_root: Path) -> Dict[str, ProductChain]:
    built_prod_chains = {}

    for prod_chain in product_chain_dicts:
        chain_id = prod_chain['id']
        chain_params = prod_chain['params']

        built_name = chain_params.get('name', None)
        built_chain_data = Path(chain_params['chain_data'])  # mandatory parameter, can't be null
        built_xls_sheet = chain_params.get('xls_sheet', None)
        built_outdir = chain_params.get('outdir', None)
        built_unit_library_id = chain_params.get('unit_library_id', None)
        built_unit_library = unit_libraries[built_unit_library_id] if built_unit_library_id is None else None

        # make sure chain_data is relative to '<bbcfg.scenario_root>/data'
        chain_data_rel = scenario_root / 'data' / built_chain_data

        built_chain = ProductChain(
            chain_data=chain_data_rel,
            name=built_name, xls_sheet=built_xls_sheet, outdir=built_outdir, units_df=built_unit_library,
        )
        built_prod_chains[chain_id] = built_chain

    return built_prod_chains


def __build_factories(factory_dicts, unit_libraries, scenario_root: Path) -> Dict[str, Factory]:
    built_factories = {}

    for factory in factory_dicts:
        fac_id = factory['id']
        fac_params = factory['params']

        built_name = fac_params.get('name', None)
        built_chain_list_file = Path(fac_params['chain_list_file'])  # mandatory parameter, can't be null
        built_chain_list_sheet = fac_params.get('chain_list_sheet', None)
        built_connections_sheet = fac_params.get('connections_sheet', None)
        built_outdir = fac_params.get('outdir', None)
        built_unit_library_id = fac_params.get('unit_library_id', None)
        built_unit_library = unit_libraries[built_unit_library_id] if built_unit_library_id is None else None

        # make sure chain_list_file is relative to '<bbcfg.scenario_root>/data'
        chain_list_file_rel = scenario_root / 'data' / built_chain_list_file

        built_factory = Factory(
            chain_list_file=chain_list_file_rel,
            chain_list_sheet=built_chain_list_sheet, connections_sheet=built_connections_sheet, name=built_name,
            outdir=built_outdir, units_df=built_unit_library,
        )
        built_factories[fac_id] = built_factory

    return built_factories


def __build_bbcfgs_with_defaults(config_file_dir: Path, cfgs: dict) -> Tuple[Config, Path]:
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

    built_emissions = cfgs.get('emissions', defcfgs.emissions)
    built_cfg.emissions = built_emissions

    built_scenario_default = cfgs.get('scenario_default', defcfgs.scenario_default)
    built_cfg.scenario_default = built_scenario_default

    # If paths_convention is present, build according to convention, otherwise the defaults from the source code
    built_cfg.paths = defcfgs.paths

    # default is where the config file itself resides
    scenario_root = config_file_dir

    if 'paths_convention' in cfgs.keys():
        cfgs_paths = cfgs['paths_convention']

        cfg_scenario_root = cfgs_paths.get('scenario_root', None)
        if cfg_scenario_root is not None:
            scenario_root = Path(cfgs_paths['scenario_root'])

        cfg_UP_sheet = cfgs_paths.get('unit_process_library_sheet', None)
        built_UP_sheet = defcfgs.paths.unit_process_library_sheet if cfg_UP_sheet is None else cfg_UP_sheet

        cfg_var_filename_prefix = cfgs_paths.get('var_filename_prefix', None)
        built_var_filename_prefix = defcfgs.paths.var_filename_prefix if cfg_var_filename_prefix is None else cfg_var_filename_prefix

        cfg_calc_filename_prefix = cfgs_paths.get('cfg_calc_filename_prefix', None)
        built_calc_filename_prefix = defcfgs.paths.calc_filename_prefix if cfg_calc_filename_prefix is None else cfg_calc_filename_prefix

        cfg_same_xls = cfgs_paths.get('same_xls', None)
        built_same_xls = defcfgs.paths.same_xls if cfg_same_xls is None else cfg_same_xls

        cfg_path_outdir_suffix = cfgs_paths.get('path_outdir_suffix', None)
        built_path_outdir_suffix = datetime.now().strftime("%Y%m%dT%H%M") if cfg_path_outdir_suffix is None else cfg_path_outdir_suffix

        cfg_UP_filesuffix = cfgs_paths.get('unit_process_library_file_suffix', None)
        built_UP_filesuffix = Path('unitlibrary.csv') if cfg_UP_filesuffix is None else cfg_UP_filesuffix

        built_cfg.paths = PathConfig.convention_paths_scenario_root(
            scenario=scenario_root,
            unit_process_library_sheet=built_UP_sheet,
            var_filename_prefix=built_var_filename_prefix,
            calc_filename_prefix=built_calc_filename_prefix,
            same_xls=built_same_xls,
            unit_process_library_file_suffix=built_UP_filesuffix,
            path_outdir_suffix=built_path_outdir_suffix,
        )

    if 'shared_var' in cfgs.keys():
        cfgs_shared_var = cfgs['shared_var']

        cfg_path_shared_fuels = cfgs_shared_var.get('path_shared_fuels', None)
        built_path_shared_fuels = defcfgs.shared_var.path_shared_fuels if cfg_path_shared_fuels is None else Path(cfg_path_shared_fuels)

        cfg_path_shared_upstream = cfgs_shared_var.get('path_shared_upstream', None)
        built_path_shared_upstream = defcfgs.shared_var.path_shared_upstream if cfg_path_shared_upstream is None else Path(cfg_path_shared_upstream)

        # (ab)using short-circuit and duck-typing here, None is falseish and bool(y) == True implies that (x and y) == y
        path_shared_fuels_rel = built_path_shared_fuels and (scenario_root / 'data' / built_path_shared_fuels)
        path_shared_upstream_rel = built_path_shared_upstream and (scenario_root / 'data' / built_path_shared_upstream)
        built_shared_var = SharedVarConfig.convention_sharedvar_scenario_root(
            path_shared_fuels=path_shared_fuels_rel,
            path_shared_upstream=path_shared_upstream_rel,
        )

        if 'fuel_dict' in cfgs_shared_var:
            cfgs_fuel_dict = cfgs_shared_var['fuel_dict']

            cfg_filepath = cfgs_fuel_dict.get('filepath', None)
            built_filepath = defcfgs.shared_var.fuel_dict['filepath'] if cfg_filepath is None else Path(cfg_filepath)

            cfg_sheet = cfgs_fuel_dict.get('sheet', None)
            built_sheet = defcfgs.shared_var.fuel_dict['sheet'] if cfg_sheet is None else cfg_sheet

            cfg_lookup_var = cfgs_fuel_dict.get('lookup_var', None)
            built_lookup_var = defcfgs.shared_var.fuel_dict['lookup_var'] if cfg_lookup_var is None else cfg_lookup_var

            filepath_rel = built_filepath and (scenario_root / 'data' / built_filepath)
            built_shared_var.fuel_dict = dict(
                filepath=filepath_rel,
                sheet=built_sheet,
                lookup_var=built_lookup_var,
            )

        built_cfg.shared_var = built_shared_var

    return built_cfg, scenario_root


Commands = List[Dict[str, dict]]

@dataclass
class Entities:
    unit_libraries: Dict[str, pd.DataFrame]
    unit_processes: Dict[str, UnitProcess]
    product_chains: Dict[str, ProductChain]
    factories: Dict[str, Factory]


def __validate_scenario_dict(config_file_dir: Path, scenario_dict: dict) -> Tuple[Config, Entities, Commands]:
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
            elif k == 'factory_balance' or k == 'factory_run_scenarios':
                if elem_id in [f['id'] for f in factory_dicts]:
                    validated_commands += [{k: c[k]}]
                else:
                    error_list += [f"WARNING: Factory '{elem_id}' mentioned in commands but not declared."]
            else:
                pass

    # All the sections EXCEPT commands may have defaults (omitted in the YAML) that we fill in
    built_cfgs, scenario_root = __build_bbcfgs_with_defaults(config_file_dir, cfgs_dict)

    # Must set the global bbcfgs before doing anything else in the library (that's the protocol)
    blackblox.dataconfig.bbcfg = built_cfgs

    built_unit_libraries = __build_unit_libraries(unit_library_dicts, scenario_root)

    built_unit_processes = __build_unit_processes(unit_process_dicts, built_unit_libraries, scenario_root)
    built_product_chains = __build_product_chains(product_chain_dicts, built_unit_libraries, scenario_root)
    built_factories = __build_factories(factory_dicts, built_unit_libraries, scenario_root)

    # TODO: cause exception on validation errors list non empty?

    built_entities = Entities(
        unit_libraries=built_unit_libraries,
        unit_processes=built_unit_processes,
        product_chains=built_product_chains,
        factories=built_factories
    )

    return built_cfgs, built_entities, validated_commands


def __run_validated_dict(cfg: Config, entities: Entities, commands: Commands):
    unit_libraries = entities.unit_libraries
    unit_processes = entities.unit_processes
    product_chains = entities.product_chains
    factories = entities.factories

    print(dedent("""\
        Time of scenario execution = {}
        Scenario uses unit process data from (full path) = "{}"
        Outputting any files to directory (full path) = "{}"

    """.format(
            cfg.timestamp_str,
            cfg.paths.unit_process_library_file.resolve(),
            cfg.paths.path_outdir.resolve(),
        )
    ))

    # commenting this out as it ends up printing a giant list of df_fuels - onee for each aliaas in the lookup_var dictionary
    # print(dedent("""\
    #     Configuration
    #     -------------
    #     Here are the configuration key/values setup in this scenario
    #     (when values were not present in the configuration file, they were obtained from 'dataconfig_defaults.py').

    #     {}
    # """.format(
    #         pformat(cfg, width=100)
    #     )
    # ))

    for cmd in commands:
        # Each command is a dict with single key (command type) and a single value (dict with params)
        cmdtype = next(iter(cmd.keys()))
        cmdparams = cmd[cmdtype]

        print(f"Command type: {cmdtype}")
        print(f"Command parameters:\n {pformat(cmdparams, width=100)}")

        # TODO: Now we are not considering any parameters OPTIONAL.
        # TODO: This will become possible when the default params are None in the balance/run_scenarios/etc. functions

        # The id parameter is always present regardless of command type
        entity_id = cmdparams.pop('id')

        if cmdtype == 'unit_process_balance':
            up = unit_processes[entity_id]
            up.balance(
                **cmdparams
                # qty=cmdparams['qty'],
                # scenario=cmdparams['scenario'],
                # write_to_console=cmdparams['write_to_console'],
            )

        elif cmdtype == 'unit_process_run_scenarios':
            up = unit_processes[entity_id]
            up.run_scenarios(
                 **cmdparams
                # scenario_list=cmdparams['scenario_list'],
                # write_to_console=cmdparams['write_to_console'],
            )

        elif cmdtype == 'product_chain_balance':
            chain = product_chains[entity_id]

            cfg_prod = cmdparams.get('product', None)
            built_prod = False if cfg_prod is None else cfg_prod
            cfg_scenario = cmdparams.get('scenario', None)
            built_scenario = blackblox.dataconfig.bbcfg.scenario_default if cfg_scenario is None else cfg_scenario

            chain.balance(
                 **cmdparams
                # qty=cmdparams['qty'],
                # write_to_console=cmdparams['write_to_console'],
                # product=built_prod,
                # scenario=built_scenario,
            )

        elif cmdtype == 'product_chain_run_scenarios':
            chain = product_chains[entity_id]
            chain.run_scenarios(
                 **cmdparams
                # scenario_list=cmdparams['scenario_list'],
                # write_to_console=cmdparams['write_to_console'],
            )

        elif cmdtype == 'factory_balance':
            factory = factories[entity_id]
            factory.balance(
                **cmdparams
                # product_qty=cmdparams['product_qty'],
                # product=cmdparams['product'],
                # product_io=cmdparams['product_io'],
                # product_unit=cmdparams['product_unit'],
                # write_to_xls=cmdparams['write_to_xls'],
                # write_to_console=cmdparams['write_to_console']
            )

        elif cmdtype == 'factory_run_scenarios':
            factory = factories[entity_id]
            factory.run_scenarios(
                **cmdparams
            )

        else:
            print(f"COMMAND TYPE \"{cmdtype}\" NOT RECOGNIZED. Ignoring...")
