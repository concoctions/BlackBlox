# Input Data Defaults
This page gives examples of the default input data conventions and column headers used in blackblox.py


## Default file structure

```
project/
├─ config.yaml
├─ data/
│  ├─ unitlibrary.csv
│  ├─ fuels.csv
|  ├─ upstream.xlsx
│  ├─ units/
│  │  ├─ var_units.xlsx
│  │  ├─ calc_units.xlsx
│  │  ├─ units_subfolder/
│  │  │  ├─ var_unitA.csv
│  │  │  ├─ calc_unitA.csv
```

## Default column headers

Column headers are not case sensitive. They are, however, space sensitive. Columns an with headers beginning with `meta` and are ignored by blackblox.py

### Unit Library

By default, the unit library is a csv file residing at `data/unitlibrary.csv`

| id | display name | product | productType |
|---|---|---|---|
| clinker_kiln | kiln | clinker | outflow |
| cement_blender | blender | cement | outflow |
| meal_mixer | mixer | meal | outflow |
| electricity | electricity generation | electricity | outflow |
| gas_scrubber | SCR flue gas cleaning | flue gas | inflow |

### Calculations Table

Calculation tables can be in Excel files or .csv, .tsv, files in in the `data` folder or a subfolder of `data`. Note that blackblox.py will only look in a single-level of subfolder.

| KnownQty   | k_QtyFrom | UnknownQty  | u_QtyTo | Calculation  | Variable    |
|------------|-----------|-------------|---------|--------------|-------------|
| clinker    | outflow    | CaO         | tmp     | Ratio        | CaO_in_Clinker |
| CaO        | tmp       | CaCO3       | inflow     | MolMassRatio | 1        |
| CaCO3      | inflow       | clay        | inflow   | Remainder        | CaCO3_in_Meal  |
| CaCO3      | tmp       | CO2       | emission  | MolMassRatio |         |
| clinker    | outflow    | fuel  | tmp     | inflow        | fuelDemand  |
| fuelDemand | inflow       | energy_from_fuel     | outflow   | Combustion   | combustEff  |
| clinker    | outflow    | electricity | inflow   | Ratio        | elecDemand  |


### Variable Table

Calculation tables can be in Excel files or .csv, .tsv, files in in the `data` folder or a subfolder of `data`. Note that blackblox.py will only look in a single-level of subfolder.

Note: only `scenario` is a pre-defined column header. The rest should align to variables specified in your own Calculations Table.

| scenario   | fuelDemand      | fuelType | CaO_in_Clinker | CaCO3_in_Meal | combustEff | elecDemand     |
|------------|-----------------|----------|-------------|------------|------------|----------------|
| meta-units | (mj /t clinker) | name     | (t/t)       | (t/t)      | (%)        | (mj/t clinker) |
| default    | 3             | coal     | 0.65       | 0.8        | 1          | 0.1            |
| EU-old | 3.6            | coal     | 0.75        | 0.8        | 1          | 0.2            |
| EU-bat_bio | 3          | charcoal | 0.65        | 0.8        | 1          | 0.1            |
| EU-typical | 3.2        | coal     | 0.67        | 0.8        | 1          | 0.1            |

## Chain Table

| Inflow  | Process_ID | Outflow |
|---------|---------|---------|
| CaCO3   | mixer   | meal    |
| meal    | kiln    | clinker |
| clinker | blender | cement  |


## Factory Tables

### Chain List Tables

- If a "chain" consists of a single process, the text `this unit only` can be entered into the `ChainFile` column. 
- `ChainSheet` is optonal, and only required if the `ChainFile` is an Excel sheet.
- If the `ChainSheet` is in the same Excel files as the Chain List, `here` can be entered into the `ChainFile` column.

| ChainName  | ChainProduct | Product_IO | ChainFile | ChainSheet   |
|------------|--------------|------------|-----------|--------------|
| cement     | cement       | outflow    | here      | Cement Chain |
| CO2capture | CO2          | inflow     | here      | CO2 Capture  |
| power      | electricity  | outflow    | here      | Power Chain  |

### Connection Tables

- `chain`, `unit`, `flowtype`, and `product name` (whether the flow is an inflow our outflow of the unit process) must be specified for both the origin flow and destination flow
- origin product name and destination product name do not have to be the same.
- Xonnections can also be made for the outflow/inflow of the entire chain, e.g, all electricity demand in all unit processes in a chain. This can be specified using `all` in the `o unit` column.

| o chain | o unit     | o flowtype | o product   | d product   | d chain | d flowtype | 
| ------- | ---------- | ---------- | ----------- | ----------- | ------- | ---------- | 
| cement  | all        | inflow     | electricity | electricity | power   | outflow    | 
| cement  | demo_kiln  | outflow    | waste heat  | steam       | power   | inflow     | 

## Lookup Tables


### Fuel Table

- A Fuel table is required to use the `combustion` calculation type. By default, the fuels table should live at `data/fuels.csv`.
- `fuel type` and `LHV` are the required columns. Emissions, if used can be specified in additional columns, as desired.

| fuel type | LHV | CO2__fossil | CO2__bio | meta-source |
|---|---|---|---|---|
| meta-units | (GJ/dry tonne) | (t/t combusted) | (t/t combusted) |  |
| heavy fuel oil | 40.4 | 3.127 | 0 | IPCC emission factor database |
| coal | 25.8 | 2.4794 | 0 | IPCC emission factor database |
| natural gas | 48 | 2.6928 | 0 | IPCC emission factor database |
| charcoal | 29.5 | 0 | 3.304 | IPCC emission factor database |
| coke | 28.2 | 3.0174 | 0 | IPCC emission factor database |

