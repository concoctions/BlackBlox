# Running blackblox from the command line

Some basic functionality of blackblox can be run from the command line, without needing to write your own Python script.

`UnitProcess.balance()` and `Factory.balance()` can be run directly, with options to specify the scenario and quantity.

Changing the default configuration options or running other functions can be done using a YAML file.

## Organizing your data

To run blackblox from the command line, it's important that your data adheres to the [standard data structure](defaults.md). Any changes to default filepaths, filenames, or column headers need to be indicated in the configration YAML.


## Available commands

### `blackblox`
Executes the commands specified in the `config.yaml` file in the directory where the command is run.

### `blackblox --config filepath_to_configfile`
Executes the commands specified in the `.yaml` file specified.

### `blackblox --unit unit_id`
Solves mass balance for a single unit process, specified by its unit id, as listed in the unit library file. Default to balance on the `default` scenario with a balance quantity of `1.0`.

The optional command argument `--s` can be used to speficy a different scenario and `--q` can be used to specify a different balance quantity.

### `blackblox --factory filepath_to_factory_Excel_file`

Solves mass balance for a factory, that exists in an excel file at the specified excel file. This command excepts that the Excel file will have a `connections` sheet and a `chains` sheet. Default to balance on the `default` scenario with a balance quantity of `1.0`.

The optional command argument `--s` can be used to speficy a different scenario and `--q` can be used to specify a different balance quantity.

### `blackblox --get_defaults`

Lists the defualt parameters and column names used by blackblox and specifies what is changable in a configuration YAML

## The Config YAML

The YAML can be used to:

- edit the blackblox configuration defaults
- create unit processes, chains, and factories
- solve model balances for unit processes, chains, and factories for a single scenario or comparatively for multiple scenarios

See the [demonstration data set](data.md) for an example of available YAML commands.
