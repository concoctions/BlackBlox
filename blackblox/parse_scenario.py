from pathlib import Path

import yaml


def run_scenario_file(filename: Path):
    with open(filename, 'r') as f:
        scenario_dict = yaml.load(f, Loader=yaml.FullLoader)
        validated_dict = __validate_scenario_dict(scenario_dict)

        __run_validated_dict(validated_dict)


def __fill_defaults(cfgs: dict, unit_libraries, unit_processes, product_chains, factories):
    return {
        'bbcfg': cfgs,
        'unit_libraries': unit_libraries,
        'unit_processes': unit_processes,
        'product_chains': product_chains,
        'factories': factories,
    }


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
    filled_defaults = __fill_defaults(cfgs, unit_libraries, unit_processes, product_chains, factories)

    # TODO: remove debug
    print(f"Validation errors: {error_list}")
    for c in validated_commands:
        print(c)

    validated = filled_defaults | {'commands': validated_commands}
    return validated


def __run_validated_dict(validated_dict: dict):
    pass
