import argparse
from pathlib import Path, PosixPath
import pprint
from types import NoneType

from blackblox.parse_scenario import run_scenario_file
import blackblox.unitprocess as uni
import blackblox.factory as fac
from blackblox.dataconfig import bbcfg


def main():
    parser = argparse.ArgumentParser(description='Use the BlackBlox library to run a scenario described in a config file (YAML).')
    parser.add_argument('--config', '--c', help='Path to scenario config file (default: \'./config.yaml\')')
    parser.add_argument('--u', '--unit', help='Specify unit by unit_id from unit library. Runs unit specified on default parameters.')
    parser.add_argument('--f', '--factory', help='Specify filename of a factory Excel file with sheets "chains" and "connections". Runs unit specified on default parameters.')
    parser.add_argument('--s', '--scenario', help='Specify scenario for --u or --f command.')
    parser.add_argument('--q', '--qty', help='Specify product qty for --u or --f command.')
    parser.add_argument('--d', '--get_defaults', action='store_true', help='displays YAML-configurble attributes and their defaults')

    args = parser.parse_args()


    if args.d:
        for i, j in [('user', bbcfg.user), 
                     ('scenario_default', bbcfg.scenario_default),
                     ('paths', bbcfg.paths),
                     ('columns', bbcfg.columns),
                     ('emissions', bbcfg.emissions),
                     ('fuel_flows', bbcfg.fuel_flows),
                     ('shared_var.path_shared_fuels', bbcfg.shared_var.path_shared_fuels),
                     ('shared_var.path_shared_upstream', bbcfg.shared_var.path_shared_upstream),                     
                     ]:
            if isinstance(j, (float, str, int, list, Path, PosixPath, NoneType)):
                if isinstance(j, str):
                    print_v = f'\'{j}\''
                else:
                    print_v = j
                print(f'\n{i}: {print_v}')
            else:
                print('\n', i)
                for k, v, in vars(j).items():
                    if isinstance(v, str):
                        print_v = f'\'{v}\''
                    else:
                        print_v = v
                    print(f'{k}: {print_v}')
        print('\n')



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
