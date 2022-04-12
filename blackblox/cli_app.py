import argparse
from pathlib import Path, PosixPath

from blackblox.parse_scenario import run_scenario_file
import blackblox.unitprocess as uni
import blackblox.factory as fac
from blackblox.dataconfig import bbcfg


def main():
    parser = argparse.ArgumentParser(description='Use the BlackBlox library to run a scenario described in a config file (YAML).',
                                     epilog='Further documentation and example data sets are available at concoctions.org/blackblox')
    parser.add_argument('--config', '--c', metavar='FILEPATH', help='Specify filepath to scenario config file (default: \'./config.yaml\')')
    parser.add_argument('--unit', '--u', metavar='UNIT_ID', help='Specify unit by unit_id from unit library. Balances unit on default parameters (if none otherwise specified).')
    parser.add_argument('--factory','--f', metavar='FILEPATH', help='Specify filepath of a factory Excel file with sheets "chains" and "connections". Balances unit on default parameters (if none otherwise specified).')
    parser.add_argument('--scenario', '--s', metavar='SCENAIO_NAME', help='Specify scenario for use with --unit or --factory command.')
    parser.add_argument('--qty', '--q', metavar='NUMBER', help='Specify product qty for --unit or --factory command.')
    parser.add_argument('--list_defaults', '--d', action='store_true', help='Displays YAML-configurble attributes and their defaults')

    args = parser.parse_args()


    if args.list_defaults:
        print('\nDefault configuration parameters.\nNote: default column headers currently CANNOT be changed in a configuration YAML.')
        print('\nbbcfg:')
        for i, j in [(' user:', bbcfg.user), 
                     ('  scenario_default', bbcfg.scenario_default),
                     ('  units_default',    bbcfg.units_default),
                     (' paths_convention:', bbcfg.paths),
                     (' columns:', bbcfg.columns),
                     ('  emissions', bbcfg.emissions),
                     ('  fuel_flows', bbcfg.fuel_flows),
                     ('  shared_var:\n      path_shared_fuels', bbcfg.shared_var.path_shared_fuels),
                     ('  shared_var:\n      path_shared_upstream', bbcfg.shared_var.path_shared_upstream),                     
                     ]:
            if isinstance(j, (float, str, int, list, Path, PosixPath, type(None))):
                if isinstance(j, (str, Path, PosixPath)):
                    print_v = f'\'{j}\''
                else:
                    print_v = j
                print(f'\n{i}: {print_v}')
            else:
                print('\n', i)
                for k, v, in vars(j).items():
                    if isinstance(v, (str, Path, PosixPath)):
                        print_v = f'\'{v}\''
                    else:
                        print_v = v
                    print(f'     {k}: {print_v}')
        print('\n')



    default_cfg_filename = 'config.yaml'
    default_cfg_path = Path() / default_cfg_filename

    cfg_path = default_cfg_path.resolve()
    if args.config:
        cfg_path = Path(args.config).resolve()

    print(f"Scenario file path to be used = \"{cfg_path}\"")

    balance_params = dict()
    if args.scenario:
        balance_params['scenario'] = args.s
    if args.qty:
        balance_params['product_qty'] = float(args.q)

    if args.unit:
        unit = uni.UnitProcess(args.u)
        unit.balance(write_to_console=True, **balance_params)

    elif args.factory:
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