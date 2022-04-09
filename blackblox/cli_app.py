import argparse
from pathlib import Path

from blackblox.parse_scenario import run_scenario_file
import blackblox.unitprocess as uni
import blackblox.factory as fac


def main():
    parser = argparse.ArgumentParser(description='Use the BlackBlox library to run a scenario described in a config file (YAML).')
    parser.add_argument('--config', help='Path to scenario config file (default: \'./config.yaml\')')
    parser.add_argument('--u', help='Specify unit by unit_id from unit library. Runs unit specified on default parameters.')
    parser.add_argument('--f', help='Specify filename of a factory Excel file with sheets "chains" and "connections". Runs unit specified on default parameters.')
    parser.add_argument('--s', help='Specify scenario for --u or --f command.')
    parser.add_argument('--q', help='Specify product qty for --u or --f command.')

    args = parser.parse_args()




    default_cfg_filename = 'config.yaml'
    default_cfg_path = Path() / default_cfg_filename

    cfg_path = default_cfg_path.resolve()
    if args.config:
        cfg_path = Path(args.config).resolve()

    print(f"Scenario file path to be used = \"{cfg_path}\"")

    balance_params = dict()
    if args.s:
        balance_params['scenario'] = args.s
    if args.q:
        balance_params['product_qty'] = float(args.q)

    if args.u:
        unit = uni.UnitProcess(args.u)
        unit.balance(write_to_console=True, **balance_params)

    elif args.f:
        factory = fac.Factory(args.f, 
                    name='Factory',
                    chain_list_sheet='chains', 
                    connections_sheet='connections')
        factory.balance(write_to_xls=True, write_to_console=True, **balance_params)

    else:
        if not cfg_path.exists():
            print(f"File not found: \"{cfg_path}\"")
            exit(8)
        else:
            print('Will now execute the commands according to the scenario config file...')

            run_scenario_file(cfg_path)
