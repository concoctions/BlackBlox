# What is blackblox.py?
Blackblox is an open source python3 library for constructing and solving "black box" process models. Its particular strength is allowing for rapid comparison of different scenarios of parameters. Input data can be stored in Excel workbooks or tab or comma delimited text files. Results are returned as dictionaries for use within python and written to Excel workbooks. Results can also be displayed on the terminal console. Blackblox's basic functionality can be run from the terminal without needing to write any Python script.

The basic "block" of blackblox is the **UnitProcess**, which contains the relationship between the inflows and outflows of a process or subprocess under evaluation. This block can be connected with others to form a linear **ProcessChain**. Units and chains can be further connected in a linear or branching fashion to form a **Factory** model.

For each level of model, two main functions are available:

- `balance()`: which evaluates the model based on one scenario, given a quantity and a specific flow to balance on.
- `run_scenarios()`: which evaluates the model on multiple scenarios, returning comparative results in a single table.

Each of these return the results as dictionaries or Pandas DataFrames, which can be used for further process within Python. Results can be written to the console or saved to an Excel file. 

Additionally, the **Factory**-level model has support for single-variable sensitivity analysis.

# Unit Processes
Unit processes are the smallest "block" in blackblox. Each unit process has a set of inflows and outflows and a set of specified fixed-ratio (linear) relationships between the process flows. Then, given a quantity for one inflow or outflow, the quantities of the remaining inflows and outflows can be calculated. 

![Example Unit Process](doc_assets/unit.drawio.svg)

A unit process is defined by two tables, a **calculations table** that specifies relatioships between flows, and a **variables table** that specifies the numerical values for the variable parameters used in the calculations. Extra data about unit process flows can be stored in **lookup tables**. All unit processes need to be listed in a **unit library** table, which tells blackblox where to find them.

Figure: Representation of a unit process

## Calculations Tables
The calculation tables specifies the relationships between flows in a unit process. Each row in the table:

- names two flows that have a relationship
- designates whether each flow is an inflow, outflow, or a flow internal to the process
- specifies the type of calculation that would generate the quantity of the second substance if the quantity of the first substance is known
- specifies the variable parameter (if any) used in that calculation that is the same name as a column in the variables table.

Table 1 provides an example of a calculation table for a simplified cement kiln. 
- **KnownQty** (k) and **UnknownQty** (v) contain the two substances with a known relationship.
- **k_QtyFrom** and **u_QtyTo** specify the location of each flow.
  - **inflow** or **i**: inflow of unit process. Each inflow must be uniquely named and represent a unique calculation.  
  - **outflow** or **o**: outflow of unit process. Each outflow must be uniquely named
  - **tmp** or **t**: a process-internal dictionary. This can be used for intermediate calculations and does not appear in inflows or outflows.
  - **emission** or **e**: outflow of unit process, which does not have to be unique. E.g. In our example table, both the calcination of limestone and the combustion of fuel will generate CO~2~. By specifying CO~2~ as the *u_QtyTo* location, the CO~2~ from both calculations can be added together. Emission flows cannot be used to balance the unit process.
  - **coinflow** or **c**: inflow of unit process, which does not have to be unique. Coinflows cannot be used to balance the unit process.
- **Calculation** specifies the type of calculation performed between the two flows. The calculation types must be those available in the program's calculator library, some of which are described in Table 2.  
- **Variable** (v) species the column in the Variables Table where to find the value of the variable parameter used in the calculation. It is also possible to define substance names that are "lookup variables" that allow the substance to be defined in the variables table and also have properties defined elsewhere. By default in blackblox, the flow name "fuel" is designated as a lookup variable, corresponding to the "fuelType" column in the Variables Table.

By default, flow names that begin or end with "energy", "heat", or "electricity" are assumed to be energy flows. All other flows are assumed to be mass flows.

Table: Example of blackblox calculation table for a clinker kiln

| KnownQty   | k_QtyFrom | UnknownQty  | u_QtyTo | Calculation  | Variable    |
|------------|-----------|-------------|---------|--------------|-------------|
| clinker    | outflow    | CaO         | tmp     | Ratio        | CaO_in_Clinker |
| CaO        | tmp       | CaCO3       | inflow     | MolMassRatio | 1        |
| CaCO3      | inflow       | clay        | inflow   | Remainder        | CaCO3_in_Meal  |
| CaCO3      | tmp       | CO2       | emission  | MolMassRatio |         |
| clinker    | outflow    | fuel  | tmp     | inflow        | fuelDemand  |
| fuelDemand | inflow       | energy_from_fuel     | outflow   | Combustion   | combustEff  |
| clinker    | outflow    | electricity | inflow   | Ratio        | elecDemand  |

Table: Calculation Types. (k = KnownQty, U = UnknownQty, V = variable)

| Calculation Name | Variable Parameter Type (v) | Relationship (k:u) | Description |
|------------------|-----------------------|--|-------------|
| Ratio | float | k * var = u | Multiples the known flow quantity by the variable parameter |
| Remainder | float | k * (1 - var) = u | Multiples the known flow quantity by (1 - the variable parameter). Only works if the variable parameter is less than one. |
| Returnvalue | float | k = u | Returns the known flow quantity. |
| MolMassRatio | float or none | (Molar Mass of U / Molar Mass of K) * v = U | Multiples the known flow quantity by the molar mass ratio of the unknown flow to the known flow. Requires both flows names to be valid chemical formulas. If no value for the variable is provided, it defaults to 1. | 
| Combustion | float | k (mass) * (MJ/kg of K) * v = u (energy) OR k (energy) / MJ / (1-v) = u (mass) | Using data from a separate "fuels" table, generates the energy provided by combusting a specified amount of fuel, or the fuel required to generate a specified amount of energy, as well as any specified emissions from the combustion. The variable parameter is the combustion efficiency, with the waste heat retuned as a separate flow. |
|  |  | e.g. [k OR u] (energy) * (1-v) = wast heat (as emission) | Combustion also adds the heat remaining after the combustion efficiency is applied as "waste heat" to the dictionary  |
|  |  | e.g. [k OR u] (mass) * (kg CO~2~/kg fuel) = CO~2~ (as emission) | Combustion can also look up emission factors from a separate "fuels" table (here shown for CO2, but any emission desired can be added) |
| Addition | none | k + k2 = u | Adds two known flow quantities together. Requires two columns to be added to the calculations table: `2nd Known Substance`, `2Qty Origin`  |
| Subtraction | none | k - k2 = u | Adds two known flow quantities together. Requires two columns to be added to the calculations table: `2nd Known Substance`, `2Qty Origin`  |


## Variables Tables 
The **variables table** provides the values of the variable parameters specified in the calculations table. There is one column for each of the variables named in the **calculation table**. The column name must be exactly the same as the specified variable name. Each row is a set of variable parameter values, identified by a **scenario** name.

Separating the values into their own table allows for the same unit process to be easily evaluated for multiple scenarios of parameter values (e.g. different production efficiencies or fuel types). (note: rows whose scenarios begin with "meta" are ignored by blackblax and can be used for notes. This is also true for columns whose name begins with "meta".)

Table: Example of a blackblox variables table for a hypothetical clinker kiln.

| scenario   | fuelDemand      | fuelType | CaO_in_Clinker | CaCO3_in_Meal | combustEff | elecDemand     |
|------------|-----------------|----------|-------------|------------|------------|----------------|
| meta-units | (mj /t clinker) | name     | (t/t)       | (t/t)      | (%)        | (mj/t clinker) |
| default    | 3             | coal     | 0.65       | 0.8        | 1          | 0.1            |
| EU-old | 3.6            | coal     | 0.75        | 0.8        | 1          | 0.2            |
| EU-bat_bio | 3          | charcoal | 0.65        | 0.8        | 1          | 0.1            |
| EU-typical | 3.2        | coal     | 0.67        | 0.8        | 1          | 0.1            |


## Lookup tables

Blackblox.py has the ability to get data about flows stored in other spreadsheets. By default, a "fuels" table is a lookup table that is recognized by the combustion calculation to get information about energy content and emission factors.

Table: Example Fuels Table

| fuel type | LHV | CO2__fossil | CO2__bio | meta-source |
|---|---|---|---|---|
| meta-units | (GJ/dry tonne) | (t/t combusted) | (t/t combusted) |  |
| heavy fuel oil | 40.4 | 3.127 | 0 | IPCC emission factor database |
| coal | 25.8 | 2.4794 | 0 | IPCC emission factor database |
| natural gas | 48 | 2.6928 | 0 | IPCC emission factor database |
| charcoal | 29.5 | 0 | 3.304 | IPCC emission factor database |
| coke | 28.2 | 3.0174 | 0 | IPCC emission factor database |

## Unit  Library
The unit library is a table that lets blackblox know what unit processes exist and how to identify them. It requires the columns:

- **id**: a unique identifier for the unit
- **display name**: what the unit is called in the resulting output
- **product**: the default product of the unit. This is the flow the unit will be balanced on if no other is specified
- **productType**: ("inflow" or "outflow"). Whether the default product is an inflow or outflow of the unit process.

Table: Example Unit Library

| id | display name | product | productType |
|---|---|---|---|
| clinker_kiln | kiln | clinker | outflow |
| cement_blender | blender | cement | outflow |
| meal_mixer | mixer | meal | outflow |
| electricity | electricity generation | electricity | outflow |
| gas_scrubber | SCR flue gas cleaning | flue gas | inflow |

## Storing Data

By default, blacblox looks for data in a `data/` subfolder of the working directory. Data can be in tab or comma delimited text files (.txt, .tsv, .csv) or in the sheets of an Excel workbook (.xls, .xlsx). If Excel workbooks are used, variable tables and calculation tables must be in separate workbooks.

The data folder needs to contain the unit process library, `unitlibrary.xlsx` (or .csv, .tsv, .txt) and any lookup tables, e.g. `fuels.csv`.

Blackblox will look for unit process data in the `data\` folder and its immediate subfolder. It identifies files that contain variable or calculation tables by the use of a filename prefix. By default, unit variable data files need to begin with `var_` (e.g. `var_cement.xls) and calculation data files need to begin with `calc_` (e.g. `calc_cement.txt`). 

If using delimited text files to store unit process data, the file name after the prefix should be the same as the unit id listed in the Unit Library. For example,  a process with the id `clinker_kiln` would require the files `var_clinker_kiln.csv` and `calc_clinker_kiln.csv`.

If using excel files to store unit process data, the excel file must begin with the file identifiers (e.g. `var_units.xlsx` and `calc_units.xlsx`) and the sheet names of each file must align with the unit ids from the unit library (e.g. `clinker_kiln` should appear as a sheet in each `var_units.xlsx` and `calc_units.xlsx` with the relevant variable table and calculation table, respectively).

So a valid file structure for blackblox could look something like this:

```
project/
├─ config.yaml
├─ data/
│  ├─ unitlibrary.csv
│  ├─ fuels.csv
│  ├─ units/
│  │  ├─ var_units.xlsx
│  │  ├─ calc_units.xlsx
│  │  ├─ var_unitA.csv
│  │  ├─ calc_unitA.csv
```


## Creating and balancing a unit processes  

Balancing a unit process calculates the quantity of all inflows and outflows of that unit process for a given set of variable parameters. To balance a unit process, the following information is needed: 

- the quantity of one inflow or outflow.  (if not specified, defaults to 1.0)
- the name of that inflow or outflow substance (if not specified, defaults to the product listed in the unit library)
- whether the substance is an inflow or outflow (if not specified, defaults to the productType listed in the unit library)
- the name of the scenario to use from the variables table (if not specified, defaults to `default`.)
  
After calculating all flows based on the user input, blackblox then checks for whether the mass and energy flows are balanced, and either raises an exception or, by default, creates an 'UKNOWN' balancer flow where needed. When processing combustion-type calculations, blackblox writes an "energy in combusted `fuelType`" flow to the inflows dictionary, to balance the energy of combustion. A similar balancer flow is provided for the combustion emissions. 


## Balancing a unit process in python

Unit Processes need to be created and then can be balanced. In python, the unit process can be created via: 

``blackblox.unitprocess.UnitProcess(unit_id)``

So, to create and balance the clinker kiln of our example, you could create it using

``kiln = blackblox.unitprocess.UnitProcess(clinker_kiln)``

and then balance it with 

``kiln.balance(scenario='EU-typical', qty=100)``

The results are returned as a dictionary and can be displayed in the console using `write_to_console=True` or written to an excel sheet using `write_to_xls=True`.

To compare multiple scenarios, the function `run_scenarios` can be used. By default, the results are written to an Excel file.

``kiln.run_scenarios(scenario_list=['EU-typical', 'EU-old', 'EU-bat_bio'])``

# Process Chain
A process chain is a linear set of connected unit processes, where an outflow of a preceding unit process is an inflow of the following unit process.   

![Example of a process chain](doc_assets/chain_pfd.png)


## Defining a chain
A process chain is defined by a table with a list of unit processes with an inflow and outflow to each, where the outflow of a unit process must be the inflow into the next unit process, as shown in the below table. 

Table:  Example chain table 

| Inflow  | Process_ID | Outflow |
|---------|---------|---------|
| CaCO3   | mixer   | meal    |
| meal    | kiln    | clinker |
| clinker | blender | cement  |

When the process chain is first used, an initialisation process creates each of the unit processes, if they do not already exist, and verifies that the inflows and outflows specified in the chain table exist for the corresponding unit processes. 

A process chain can be defined by specifying the location of the chain table either in an Excel workbook or delimited text file using

```
chainName = processchain.ProcessChain(chain_data='path/to/chaindata.xlsx, 
                                       xls_sheet='sheet name)
```

(`xls_sheet` is only required if using an Excel file with multiple sheets)

## Balancing a chain 

Balancing a chain calculates the quantity of all inflows and outflows of each unit process in the chain, either from first inflow to last outflow or from last outflow to first inflow. To balance a chain, the following arguments  must be provided: 
  * `qty`: the quantity of one inflow or outflow somewhere in the chain
  * `product`: the name of that inflow or outflow substance. (Attempts to default to product of last unit process, if an outflow. If not, will attempt to default to the product of the first unit process, if an inflow. )
  * `i_o`: whether the product is an inflow or outflow (defaults to the default product location)
  * `scenario` the name of the configuration scenario to use from the variables table. (defaults to "default")
  * the name of the unit process in the chain, if the specified flow is not an inflow into the first process or an outflow of the last process.
  
 All arguments besides the quantity can be optional, if a default product can be determined.
 
 Balancing a chain returns a dictionary with both the calculated inflows and outflows for each unit process, as well as the the overall inflows and outflows. The results can also be written to the console or an excel file.

## Generating a chain diagram 
After a chain has been defined, a process flow diagram of the chain can be generated automatically using 

`processName.diagram()`

Ff Graphviz has been correctly installed to your computer's path. If not, this will fail with a hopefully useful error message.

![This ProcessChain diagram was autogenerated](doc_assets/chain_pfd.png)

# Factory
A factory is a collection of one or more connected process chains, where the inflow of outflow of any unit process within any chain can be the inflow or outflow of any other chain. A factory has a single main chain, and zero or more auxiliary chains. By specifying an input or output quantity to the main chain, it is possible to calculate the inflows and outflows of all processes within the chain.

## Defining a factory
A factory is defined by two tables: one that lists the chains (and their file locations) and another that lists the connections between the chains. Factory data can be in separate tab delimited text files or in a single excel workbook.

### Factory chains table
This table specifies the location of the process chain data used in the factory, as well as the  primary product and whether that product is an inflow or outflow of the chain.

The first chain of the chain list is assumed to be the main product chain, but otherwise it doesn't matter.
The chains can either be in the same file, if an excel workbook, or in a separate file.

Table: Example of a Factory Chains Table

| ChainName  | ChainProduct | Product_IO | ChainFile | ChainSheet   |
|------------|--------------|------------|-----------|--------------|
| cement     | cement       | outflow    | here      | Cement Chain |
| CO2capture | CO2          | inflow     | here      | CO2 Capture  |
| power      | electricity  | outflow    | here      | Power Chain  |
 
### Factory connections table
The factory connections table specifies how the chains connect, including the origin process chain and unit process, the destination chain, the connecting product, and whether the product is an inflow or outflow of the origin and destination.
The connections table is order dependent, and the first chain should always be the main chain. 

Table: Example of a Factory Connections Table

| OriginChain | OriginProcess | Product     | Product_IO_of_Origin | Product_IO_of_Destination | DestinationChain |
|-------------|---------------|-------------|----------------------|---------------------------|------------------|
| cement      | kiln          | CO2         | outflow              | inflow                    | CO2capture       |
| cement      | all           | electricity | inflow               | outflow                   | power            |
| CO2capture  | all           | electricity | inflow               | outflow                   | power            |


If the destination is not the start or end of a chain, an optional `destination process` column can be used. This column is also used when specifying recycling connections. Currently two types of recycling are usable:

- *1-to-1 replacement*: allows for a recycle flow to replace a flow in another unit process, given that is a 1-to-1 correspondent and does not affect other flows in unit process.
- *energy replacing fuel*: allows for recycled energy to replace energy generated from a fuel in a unit process that has a combustion calculation. The emission outflows (e.g. CO~2~) and inflow of oxygen are also recalculated.

If there is a greater quantity of the recycled flow than is used in the destination process, the remainder is treated as a normal output.  A single flow can be recycled into multiple units, by specifying each connection as a new line in the table.  If there is insufficient recycling flow to fully replace the existing flow, it is only partially replaced.

## Balancing a factory
By default, the factory is balanced on a quantity of the product of the main ProductChain, and uses a single scenario of variables for the whole factory. `factory.balance()` takes the same parameters as `productchain.balance()`. Additionally, the factory can be balanced in other products from the main chain by passing `product`, `product_unit`, `product_io` parameters. A factory cannot be balanced on auxiliary chains.

Balancing a factory returns a nested dictionary with the inflows and outflows of the factory, every chain, and every unit process. By default, the results are saved to an Excel workbook with sheets for:

  - Total factory inflows and outflows
  - A matrix for all inflow from every unit process
  - A matrix for all outflows from every unit process
  - A list of all internal flows/connections, both within chains and
  - Inflows for each chain unit process and chain totals (per chain)
  - Outflows for each chain unit process and chain totals (per chain)

By default, the data is divided into mass and energy flows, if energy flow name signifiers are provided, with totals for both mass and energy flows.

## Generating a factory diagram 
After a factory has been defined, a process flow diagram of the factory can be generated. However, due to the limitations of the diagram rendering software, they are unlikely to be pretty. Graphviz must be properly installed for this to work.
  
![Example of an auto-generated factory digram](doc_assets/factory_pfd.png)

## Sensitivity Analyses
A single-variable sensitivity analysis can also be run on a Factory model.  The `factory.run_sensitivity()` function takes all the same parameters as `factory.balance()` as well as:

- `unit_name`: (str) the identifier of the **UnitProcess** containing the variable of interest
- `chain_name`: (str) the **ProcessChain** containing the unit of interest
- `variable`: (str) the variable of interest, which should correspond to a column in the unit's **Variable Table**
- `variable_options`: a list of the variables options to be calculated.

The sensitivity analysis returns an Excel workbook with results for each variable option in columns.

# Where to Find blackblox.py
Blackblox.py is an free and open source library released under the GNU General Public License v3 (GPLv3). Blackblox is under active development. Currently available features and documentation may be different than what is provided in this Appendix.

- Full documentation for blackblox can be found at the project homepage: https://concoctions.org/blackblox/
- Source code and data are available on GitHub: https://github.com/concoctions/BlackBlox
- Blackblox can be installed using `pip install blackblox`. Information about the package can be found at PyPi: https://pypi.org/project/blackblox/
