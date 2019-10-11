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
                 "project": f"BECCS Steel - {datetime.now().strftime('%d %B %Y')}",
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
outdir = f'output/steel_{today}'

# for chain, factory, and industry tests
view_diagrams = False
save_diagrams = True

# for factory and industry tests
write_to_xls = True

# for multi-scenario factory tests
individual_xls = True


###############################################################################
# TESTS
###############################################################################

qty = 1.0


###############################################################################
# BLAST FURNACE STEELMAKING

BF_factory_dict = {
                'IBC-0C': dict(chain_list_file="data/steel/factories/IBF_factory-0C.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-0C",
                                        scenario='BBF-0B'),
                'IBC-LC': dict(chain_list_file="data/steel/factories/IBF_factory-LC.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-LC",
                                        scenario='BBF-0B'),
                'IBC-HC': dict(chain_list_file="data/steel/factories/IBF_factory-HC.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-HC",
                                        scenario='BBF-0B'),
}

dat.outdir = f'{outdir}/BF/No Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-0B', 'TGR-0B', 'HIS-0B'], 
                        upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                        upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BF/No Biomass')


dat.outdir = f'{outdir}/BF/Low Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-LB', 'TGR-LB', 'HIS-LB',], 
                        upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                        upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BF/Low Biomass')


dat.outdir = f'{outdir}/BF/High Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-HB', 'TGR-HB', 'HIS-HB',], 
                        upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                        upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BF/High Biomass')




###############################################################################
# DIRECT REDUCTION STEELMAKING

DRI_factory_dict = {
                'DRI-0C': dict(chain_list_file="data/steel/factories/DRI_factory-0C.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF-0C",
                                        scenario='MID-0B'),
                'DRI-LC': dict(chain_list_file="data/steel/factories/DRI_factory-LC.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF-LC",
                                        scenario='MID-0B'),
                'DRI-HC': dict(chain_list_file="data/steel/factories/DRI_factory-HC.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF-HC",
                                        scenario='MID-0B'),
}

dat.outdir = f'{outdir}/DRI/No Biomass'

com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['MID-0B', 'ULC-0B'], 
                        upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                        upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/DRI/No Biomass')


dat.outdir = f'{outdir}/DRI/Low Biomass'

com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['MID-LB', 'ULC-LB'], 
                        upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                        upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/DRI/Low Biomass')


dat.outdir = f'{outdir}/DRI/High Biomass'

com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['MID-HB', 'ULC-HB'], 
                        upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                        upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/DRI/High Biomass')

# ###############################################################################
# SENSITIVITY ANALYSES


# electricity mix
ibf_subdirs = ['No Biomass/BBF', 'No Biomass/TGR', 'No Biomass/HIS', 'High Biomass/BBF', 'High Biomass/TGR', 'High Biomass/HIS']
ibf_elec_scenarios = ['BBF-0B', 'TGR-0B', 'HIS-0B', 'BBF-HB', 'TGR-HB', 'HIS-HB']

elec_inflow_dict = iof.nested_dicts(3)
elec_outflow_dict = iof.nested_dicts(3)

for i in range(len(ibf_elec_scenarios)):
    dat.outdir = f'{outdir}/Electricity/{ibf_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBC-0C', 'IBC-HC'], 
                                scenario=ibf_elec_scenarios[i],
                                chain_name='power', 
                                unit_name='simple_power', 
                                variable='fueltype', 
                                variable_options=['natural gas - IPCC', 'electricity PROXY - EU 2016', 'electricity PROXY - CN 2016', 'electricity PROXY - decarbonized',],
                                fixed_vars=[('combustion eff', 1.0)],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/Electricity/{ibf_subdirs[i]}')

    for flow in inflow_dict:
        for scen in inflow_dict[flow]:
            for fact in inflow_dict[flow][scen]:
                elec_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                elec_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]



dri_subdirs = ['No Biomass/MID', 'No Biomass/ULC','High Biomass/MID', 'High Biomass/ULC',]
dri_elec_scenarios = ['MID-0B', 'ULC-0B', 'MID-HB', 'ULC-HB',]
for i in range(len(dri_elec_scenarios)):
    dat.outdir = f'{outdir}/Electricity/{dri_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-HC'], 
                                scenario=dri_elec_scenarios[i],
                                chain_name='power', 
                                unit_name='simple_power', 
                                variable='fueltype', 
                                variable_options=['natural gas - IPCC', 'electricity PROXY - EU 2016', 'electricity PROXY - CN 2016', 'electricity PROXY - decarbonized'],
                                fixed_vars=[('combustion eff', 1.0)],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/Electricity/{dri_subdirs[i]}')

    for flow in inflow_dict:
                for scen in inflow_dict[flow]:
                    for fact in inflow_dict[flow][scen]:
                        elec_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                elec_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]              


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


# # HIsarna energy use
his_subdirs = ['No Biomass', 'High Biomass']
his_fuel_scenarios = ['HIS-0B','HIS-HB']

his_inflow_dict = iof.nested_dicts(3)
his_outflow_dict = iof.nested_dicts(3)

for i in range(len(his_fuel_scenarios)):
    dat.outdir = f'{outdir}/HIsarna energy/{his_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBC-0C', 'IBC-HC'], 
                                scenario=his_fuel_scenarios[i],
                                chain_name='steel', 
                                unit_name='simple_BF', 
                                variable='secondary fuel demand', 
                                variable_options=[0.75, 0.61, 0.56],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/HIsarna energy/{his_subdirs[i]}')

    for flow in inflow_dict:
                for scen in inflow_dict[flow]:
                    for fact in inflow_dict[flow][scen]:
                        his_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                his_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]              

meta_df = iof.metadata_df(user=dat.user_data, 
                            name=f"simple_BF fueld demand sens", 
                            level="Factory", 
                            scenario='multi', 
                            product='default',
                            product_qty=qty, 
                            energy_flows=dat.energy_flows)
his_dfs = [meta_df]
his_sheets = ["meta"]

for flow in his_inflow_dict:
    df = iof.make_df(his_inflow_dict[flow])
    his_dfs.append(df)
    his_sheets.append(f"IN {flow}")

for flow in his_outflow_dict:
    df = iof.make_df(his_outflow_dict[flow])
    his_dfs.append(df)
    his_sheets.append(f"OUT {flow}")

iof.write_to_excel(df_or_df_list=his_dfs,
                    sheet_list=his_sheets, 
                    filedir=f"{outdir}/HIsarna energy", 
                    filename=f'HIsarna_sens{datetime.now().strftime("%Y-%m-%d_%H%M")}')

#BIOMASS Emissions
bio_inflow_dict = iof.nested_dicts(3)
bio_outflow_dict = iof.nested_dicts(3)

ibf_bio_subdirs = ['High Biomass/BBF', 'High Biomass/TGR', 'High Biomass/HIS']
ibf_bio_scenarios = [ 'BBF-HB', 'TGR-HB', 'HIS-HB',]

for i in range(len(ibf_bio_scenarios)):

    dat.outdir = f'{outdir}/biomass/{ibf_bio_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBC-0C', 'IBC-HC',], 
                                scenario=ibf_bio_scenarios[i],
                                chain_name='charcoal', 
                                unit_name='simple_charcoal', 
                                variable='total CO2', 
                                variable_options=[0.54, 1.2, 1.38, 1.73, 2.25, 2.7],
                                fixed_vars=False,
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/biomass/{ibf_bio_subdirs[i]}')

    for flow in inflow_dict:
                for scen in inflow_dict[flow]:
                    for fact in inflow_dict[flow][scen]:
                        bio_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                bio_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]      

dri_bio_subdirs = ['High Biomass/MID', 'High Biomass/ULC',]
dri_bio_scenarios = ['MID-HB', 'ULC-HB',]
for i in range(len(dri_bio_scenarios)):
    dat.outdir = f'{outdir}/biomass/{dri_bio_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-HC'], 
                                scenario=dri_bio_scenarios[i],
                                chain_name='syngas', 
                                unit_name='simple_syngas', 
                                variable='feedstock type', 
                                variable_options=['wood chips (EU no swiss, dry)', 'wood chips, RER emissions', 'wood chips, high emissions', 'wood chips, medium emissions'],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/biomass/{dri_bio_subdirs[i]}')

    for flow in inflow_dict:
                for scen in inflow_dict[flow]:
                    for fact in inflow_dict[flow][scen]:
                        bio_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                bio_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]      

meta_df = iof.metadata_df(user=dat.user_data, 
                            name=f"biofuel_prod biomass emissions", 
                            level="Factory", 
                            scenario='multi', 
                            product='default',
                            product_qty=qty, 
                            energy_flows=dat.energy_flows)
bio_dfs = [meta_df]
bio_sheets = ["meta"]

for flow in bio_inflow_dict:
    df = iof.make_df(bio_inflow_dict[flow])
    bio_dfs.append(df)
    bio_sheets.append(f"IN {flow}")

for flow in bio_outflow_dict:
    df = iof.make_df(bio_outflow_dict[flow])
    bio_dfs.append(df)
    bio_sheets.append(f"OUT {flow}")

iof.write_to_excel(df_or_df_list=bio_dfs,
                    sheet_list=bio_sheets, 
                    filedir=f"{outdir}/biomass", 
                    filename=f'biomass_sens{datetime.now().strftime("%Y-%m-%d_%H%M")}')

#Syngas type
gas_inflow_dict = iof.nested_dicts(3)
gas_outflow_dict = iof.nested_dicts(3)

dri_subdirs = ['High Biomass/MID', 'High Biomass/ULC',]
dri_gas_scenarios = ['MID-HB', 'ULC-HB',]
for i in range(len(dri_gas_scenarios)):
    dat.outdir = f'{outdir}/syngasLHV/{dri_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-HC'], 
                                scenario=dri_gas_scenarios[i],
                                chain_name='steel', 
                                unit_name='simple_DRI', 
                                variable='biofuel type', 
                                variable_options=['syngas - wood', 'syngas - ecoinvent', 'syngas - PNNL'],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/syngasLHV/{dri_subdirs[i]}')

    for flow in inflow_dict:
                for scen in inflow_dict[flow]:
                    for fact in inflow_dict[flow][scen]:
                        gas_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                gas_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]      

meta_df = iof.metadata_df(user=dat.user_data, 
                            name=f"syngas type", 
                            level="Factory", 
                            scenario='multi', 
                            product='default',
                            product_qty=qty, 
                            energy_flows=dat.energy_flows)
gas_dfs = [meta_df]
gas_sheets = ["meta"]

for flow in gas_inflow_dict:
    df = iof.make_df(gas_inflow_dict[flow])
    gas_dfs.append(df)
    gas_sheets.append(f"IN {flow}")

for flow in gas_outflow_dict:
    df = iof.make_df(gas_outflow_dict[flow])
    gas_dfs.append(df)
    gas_sheets.append(f"OUT {flow}")

iof.write_to_excel(df_or_df_list=gas_dfs,
                    sheet_list=gas_sheets, 
                    filedir=f"{outdir}/syngasLHV", 
                    filename=f'syngas_sens{datetime.now().strftime("%Y-%m-%d_%H%M")}')


# alloy type
loy_inflow_dict = iof.nested_dicts(3)
loy_outflow_dict = iof.nested_dicts(3)

ibf_subdirs = ['No Biomass/BBF', 'High Biomass/BBF',]
ibf_alloy_scenarios = ['BBF-0B', 'BBF-HB',]

for i in range(len(ibf_alloy_scenarios)):
    dat.outdir = f'{outdir}/alloy/{ibf_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBC-0C', 'IBC-HC'], 
                                scenario=ibf_alloy_scenarios[i],
                                chain_name='steel', 
                                unit_name='simple_casting', 
                                variable='alloy type', 
                                variable_options=['none', 'no alloy', 'low alloy', 'chromium alloy',],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/alloy/{ibf_subdirs[i]}')

    for flow in inflow_dict:
                for scen in inflow_dict[flow]:
                    for fact in inflow_dict[flow][scen]:
                        loy_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                loy_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]      


dri_subdirs = ['No Biomass/MID', 'High Biomass/MID',]
dri_alloy_scenarios = ['MID-0B', 'MID-HB',]
for i in range(len(dri_alloy_scenarios)):
    dat.outdir = f'{outdir}/alloy/{dri_subdirs[i]}'
    inflow_dict, outflow_dict = com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-HC'], 
                                scenario=dri_alloy_scenarios[i],
                                chain_name='steel', 
                                unit_name='simple_casting', 
                                variable='alloy type', 
                                variable_options=['no alloy', 'low alloy', 'chromium alloy',],
                                scenario_product=False,
                                scenario_unit=False,
                                scenario_io=False,
                                qty=qty, 
                                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'],
                                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                                write_to_console=write_to_console, 
                                write_to_xls=write_to_xls,
                                view_diagrams=view_diagrams,
                                save_diagrams=save_diagrams,
                                outdir=f'{outdir}/alloy/{dri_subdirs[i]}')

    for flow in inflow_dict:
                for scen in inflow_dict[flow]:
                    for fact in inflow_dict[flow][scen]:
                        loy_inflow_dict[flow][scen][fact] = inflow_dict[flow][scen][fact]

    for flow in outflow_dict:
        for scen in outflow_dict[flow]:
            for fact in outflow_dict[flow][scen]:
                loy_outflow_dict[flow][scen][fact] = outflow_dict[flow][scen][fact]      

meta_df = iof.metadata_df(user=dat.user_data, 
                            name=f"alloy type", 
                            level="Factory", 
                            scenario='multi', 
                            product='default',
                            product_qty=qty, 
                            energy_flows=dat.energy_flows)
loy_dfs = [meta_df]
loy_sheets = ["meta"]

for flow in loy_inflow_dict:
    df = iof.make_df(loy_inflow_dict[flow])
    loy_dfs.append(df)
    loy_sheets.append(f"IN {flow}")

for flow in loy_outflow_dict:
    df = iof.make_df(loy_outflow_dict[flow])
    loy_dfs.append(df)
    loy_sheets.append(f"OUT {flow}")

iof.write_to_excel(df_or_df_list=loy_dfs,
                    sheet_list=loy_sheets, 
                    filedir=f"{outdir}/alloy", 
                    filename=f'alloy_sens{datetime.now().strftime("%Y-%m-%d_%H%M")}')