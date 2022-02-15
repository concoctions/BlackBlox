import argparse
from pathlib import Path

from blackblox.parse_scenario import run_scenario_file


def main():
    parser = argparse.ArgumentParser(description='Use the BlackBlox library to run a scenario described in a config file (YAML).')
    parser.add_argument('--config', help='Path to scenario config file (default: \'./config.yaml\')')

    args = parser.parse_args()

    default_cfg_filename = 'config.yaml'
    default_cfg_path = Path() / default_cfg_filename

    cfg_path = default_cfg_path.resolve()
    if args.config:
        cfg_path = Path(args.config).resolve()

    print(f"Scenario file path to be used = \"{cfg_path}\"")

    if not cfg_path.exists():
        print(f"File not found: \"{cfg_path}\"")
        exit(8)
    else:
        print('Will now execute the commands according to the scenario config file...')

        run_scenario_file(cfg_path)
