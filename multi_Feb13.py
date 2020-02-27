"""GENERATE RESULTS
"""

import compute as com
import dataconfig as dat
import io_functions as iof
from datetime import datetime
from collections import defaultdict
import importlib


################################################################################
# METADATA
################################################################################

dat.user_data = {"name": "S.E. Tanzer",
                 "affiliation": "TU Delft",
                 "project": f"BECCS Multi-Industry - {datetime.now().strftime('%d %B %Y')}",
}

dat.default_units = {'mass': 't', 
                     'energy':'GJ',
}



################################################################################
# OUTPUT
################################################################################


# for all tests
write_to_console = False
today = f'{datetime.now().strftime("%b%d")}/{datetime.now().strftime("%H%M")}'
outdir = f'output/multi_{today}'

# for chain, factory, and industry tests
view_diagrams = False
save_diagrams = True

# for factory and industry tests
write_to_xls = True
dat.outdir = f'{outdir}'

# for multi-scenario factory tests
individual_xls = True


###############################################################################
# TESTS
###############################################################################

qty = 1.0 # standardized to 1 t of product


###############################################################################
# CLINKER

clinker_factory_dict = {
                'CLK-0C': dict(chain_list_file='data/cement/factories/clinker_factory-0C.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='clinker-0C',
                                    scenario='CLK-0B'),
                'CLK-HC': dict(chain_list_file='data/cement/factories/clinker_factory-HC.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='clinker-HC',
                                    scenario='CLK-0B'),
                'CLK-CLC': dict(chain_list_file='data/cement/factories/clinker_factory-CLC.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='clinker-CLC',
                                    scenario='CLK-0B'),
}


com.test_factory_scenarios(factory_dict=clinker_factory_dict,
                        scenario_factories=['CLK-0C', 'CLK-HC', 'CLK-CLC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['CLK-0B', 'CLK-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        downstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2 removed__downstream (calcination CO2)', 'CO2__upstream', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}',
                        filename='_multi-clinker',
                        productname='clinker')

###############################################################################
# IRON

BF_factory_dict = {
                'IBF-0C': dict(chain_list_file="data/steel/factories/iron_IBF_factory-0C.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-0C",
                                        scenario='BBF-0B'),
                'IBF-HC': dict(chain_list_file="data/steel/factories/iron_IBF_factory-HC.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-HC",
                                        scenario='BBF-0B'),
}

DRI_factory_dict = {
                'DRI-0C': dict(chain_list_file="data/steel/factories/iron_DRI_factory-0C.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF-0C",
                                        scenario='MID-0B'),
                'DRI-HC': dict(chain_list_file="data/steel/factories/iron_DRI_factory-HC.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF-HC",
                                        scenario='MID-0B'),
}


com.test_factory_scenarios(factory_dict=BF_factory_dict,
                            scenario_factories=['IBF-0C', 'IBF-HC'], 
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            scenario_list=['BBF-0B', 'BBF-HB','TGR-0B', 'TGR-HB'], 
                            upstream_outflows=['CO2'], 
                            upstream_inflows=['CO2 removed'],
                            downstream_inflows=['CO2 removed'],
                            aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}',
                            filename='_multi-BF',
                            productname='iron')


com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                            scenario_factories=['DRI-0C', 'DRI-HC'], 
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            scenario_list=['MID-0B', 'MID-HB'], 
                            upstream_outflows=['CO2'], 
                            upstream_inflows=['CO2 removed'],
                            downstream_inflows=['CO2 removed'],
                            aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}',
                            filename='_multi-DRI',
                            productname='iron')

###############################################################################
# PULP

pulp_factory_dict = {
                'PLP-0C': dict(chain_list_file='data/paper/factories/pulp_factory-0C.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='pulp-0C',
                                    scenario='PLP-0B'),
                'PLP-HC': dict(chain_list_file='data/paper/factories/pulp_factory-HC.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='pulp-HC',
                                    scenario='PLP-0B'),
}


com.test_factory_scenarios(factory_dict=pulp_factory_dict,
                        scenario_factories=['PLP-0C', 'PLP-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['PLP-0B', 'PLP-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        downstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}',
                        filename='_multi-pulp',
                        productname='pulp')


###############################################################################
# ELECTRICITY SENSITIVITY ANALYSIS


elec_inflow_dict = iof.nested_dicts(3)
elec_outflow_dict = iof.nested_dicts(3)

# BLAST FURNACE IRON
ibf_scenarios = ['BBF-0B', 'BBF-HB', 'TGR-0B', 'TGR-HB']

for i in range(len(ibf_scenarios)):
    dat.outdir = f'{outdir}/Electricity/{ibf_scenarios[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBF-0C', 'IBF-HC'], 
                                scenario=ibf_scenarios[i],
                                chain_name='power', 
                                unit_name='simple_power', 
                                variable='fueltype', 
                                variable_options=['electricity 0g/kWh', 'electricity 200g/kWh', 
                                                  'electricity 400g/kWh', 'electricity 600g/kWh', 
                                                  'electricity 800g/kWh', 'electricity 1000g/kWh',],
                                fixed_vars=[('combustion eff', 1.0)],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2',],
                                upstream_inflows=['CO2 removed',],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/Electricity/{ibf_scenarios[i]}')

    for flow in inflow_dict:
        for scen in inflow_dict[flow]:
            for fact in inflow_dict[flow][scen]:
                elec_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                elec_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]


# DIRECT REDUCED IRON
dri_scenarios = ['MID-0B', 'MID-HB',]
for i in range(len(dri_scenarios)):
    dat.outdir = f'{outdir}/Electricity/{dri_scenarios[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-HC'], 
                                scenario=dri_scenarios[i],
                                chain_name='power', 
                                unit_name='simple_power', 
                                variable='fueltype', 
                                variable_options=['electricity 0g/kWh', 'electricity 200g/kWh', 
                                                  'electricity 400g/kWh', 'electricity 600g/kWh', 
                                                  'electricity 800g/kWh', 'electricity 1000g/kWh',],
                                fixed_vars=[('combustion eff', 1.0)],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2',],
                                upstream_inflows=['CO2 removed',],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/Electricity/{dri_scenarios[i]}')

    for flow in inflow_dict:
            for scen in inflow_dict[flow]:
                for fact in inflow_dict[flow][scen]:
                    elec_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                elec_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]    


# CLINKER

clinker_scenarios = ['CLK-0B', 'CLK-HB']
for i in range(len(clinker_scenarios)):
    dat.outdir = f'{outdir}/Electricity/{clinker_scenarios[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=clinker_factory_dict,
                                scenario_factories=['CLK-0C', 'CLK-HC', 'CLK-CLC'], 
                                scenario=clinker_scenarios[i],
                                chain_name='power', 
                                unit_name='simple_power', 
                                variable='fueltype', 
                                variable_options=['electricity 0g/kWh', 'electricity 200g/kWh', 
                                                  'electricity 400g/kWh', 'electricity 600g/kWh', 
                                                  'electricity 800g/kWh', 'electricity 1000g/kWh',],
                                fixed_vars=[('combustion eff', 1.0)],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2',],
                                upstream_inflows=['CO2 removed',],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/Electricity/{clinker_scenarios[i]}')

    for flow in inflow_dict:
            for scen in inflow_dict[flow]:
                for fact in inflow_dict[flow][scen]:
                    elec_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                elec_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]  

# PULP   

pulp_scenarios = ['PLP-0B', 'PLP-HB']
for i in range(len(pulp_scenarios)):
    dat.outdir = f'{outdir}/Electricity/{pulp_scenarios[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=pulp_factory_dict,
                                scenario_factories=['PLP-0C', 'PLP-HC'], 
                                scenario=pulp_scenarios[i],
                                chain_name='power', 
                                unit_name='simple_power', 
                                variable='fueltype', 
                                variable_options=['electricity 0g/kWh', 'electricity 200g/kWh', 
                                                  'electricity 400g/kWh', 'electricity 600g/kWh', 
                                                  'electricity 800g/kWh', 'electricity 1000g/kWh',],
                                fixed_vars=[('combustion eff', 1.0)],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2',],
                                upstream_inflows=['CO2 removed',],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/Electricity/{pulp_scenarios[i]}')

    for flow in inflow_dict:
            for scen in inflow_dict[flow]:
                for fact in inflow_dict[flow][scen]:
                    elec_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                elec_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]  

# Aggregated Output File

meta_df = iof.metadata_df(user=dat.user_data, 
                            name=f"simple_power fueltype sens", 
                            level="Factory", 
                            scenario='multi', 
                            product='default',
                            product_qty=qty, 
                            energy_flows=dat.energy_flows)
elec_dfs = [meta_df]
elec_sheets = ["meta"]

for flow in elec_inflow_dict:
    df = iof.make_df(elec_inflow_dict[flow])
    elec_dfs.append(df)
    elec_sheets.append(f"IN {flow}")

for flow in elec_outflow_dict:
    df = iof.make_df(elec_outflow_dict[flow])
    elec_dfs.append(df)
    elec_sheets.append(f"OUT {flow}")

iof.write_to_excel(df_or_df_list=elec_dfs,
                    sheet_list=elec_sheets, 
                    filedir=f"{outdir}/Electricity", 
                    filename=f'Electricity_sens{datetime.now().strftime("%Y-%m-%d_%H%M")}')
