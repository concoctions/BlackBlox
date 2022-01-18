from pathlib import Path
from typing import List

import yaml

import dataconfig_defaults
from dataconfig_format import Config, PathConfig
from factory import Factory
from processchain import ProductChain
from unitprocess import UnitProcess


def run_scenario_file(filename: Path):
    with open(filename, 'r') as f:
        scenario_dict = yaml.load(f, Loader=yaml.FullLoader)
        validated_dict = __validate_scenario_dict(scenario_dict)

        __run_validated_dict(validated_dict)


def __build_unit_libraries(unit_libraries):
    pass


def __build_unit_processes(unit_processes) -> List[UnitProcess]:
    pass


def __build_product_chains(product_chains) -> List[ProductChain]:
    pass


def __build_factories(factories) -> List[Factory]:
    pass


def __build_bbcfgs_with_defaults(cfgs: dict) -> Config:
    # for bbcfg basically everything is optional
    # thus we just start with the default cfg, and override ONLY what is specififed in the YAML
    built_cfg = dataconfig_defaults.default

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

    built_emissions = cfgs.get('emissions', dataconfig_defaults.default.emissions)
    built_cfg.emissions = built_emissions

    built_scenario_default = cfgs.get('scenario_default', dataconfig_defaults.default.scenario_default)
    built_cfg.scenario_default = built_scenario_default

    # If paths_convention is present, build according to convention, otherwise the defaults from the source code
    if 'paths_convention' in cfgs.keys():
        cfgs_paths = cfgs['paths_convention']

        # default is CWD
        cfg_scenario_root = cfgs_paths.get('scenario_root', None)
        built_scenario_root = Path() if cfg_scenario_root is None else Path(cfgs_paths['scenario_root'])

        cfg_unit_process_library_sheet = cfgs_paths.get('unit_process_library_sheet', None)
        built_unit_process_library_sheet = dataconfig_defaults.default.paths.unit_process_library_sheet if cfg_unit_process_library_sheet is None else cfg_unit_process_library_sheet

        # TODO the rest

    return built_cfg


def __validate_scenario_dict(scenario_dict: dict):
    # cfgs is a dictionary, all the rest are lists
    cfgs = scenario_dict.get('bbcfg', {})
    unit_libraries = scenario_dict.get('unit_libraries', [])
    unit_processes = scenario_dict.get('unit_processes', [])
    product_chains = scenario_dict.get('product_chains', [])
    factories = scenario_dict.get('factories', [])
    commands = scenario_dict.get('commands', [])

    error_list = []
    validated_commands = []

    # Check that all commands refer only to ids of actually existing entities
    for c in commands:
        for k in c.keys():  # each command is a dictionary with single key (the command name) and single value (props)
            elem_id = c[k]['id']
            if k == 'unit_process_balance' or k == 'unit_process_run_scenarios':
                if elem_id in [up['id'] for up in unit_processes]:
                    validated_commands += [{k: c[k]}]
                else:
                    error_list += [f"WARNING: Unit process '{elem_id}' mentioned in commands but not declared."]
            elif k == 'product_chain_balance' or k == 'product_chain_run_scenarios':
                if elem_id in [pc['id'] for pc in product_chains]:
                    validated_commands += [{k: c[k]}]
                else:
                    error_list += [f"WARNING: Product chain '{elem_id}' mentioned in commands but not declared."]
            elif k == 'factory_balance':
                if elem_id in [f['id'] for f in factories]:
                    validated_commands += [{k: c[k]}]
                else:
                    error_list += [f"WARNING: Factory '{elem_id}' mentioned in commands but not declared."]
            else:
                pass

    # All the sections EXCEPT commands may have defaults (omitted in the YAML) that we fill in
    filled_defaults = __fill_default_entities(cfgs, unit_libraries, unit_processes, product_chains, factories)

    # TODO: remove debug
    print(f"Validation errors: {error_list}")
    for c in validated_commands:
        print(c)

    validated = filled_defaults | {'commands': validated_commands}
    return validated


def __run_validated_dict(validated_dict: dict):
    pass
