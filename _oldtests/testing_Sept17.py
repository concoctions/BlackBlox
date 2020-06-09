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
                'IBC-0C': dict(chain_list_file="data/steel/factories/IBF_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-0C",
                                        scenario='BBF-0B'),
                'IBC-LC': dict(chain_list_file="data/steel/factories/IBF-factory-BFG CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-LC",
                                        scenario='BBF-0B'),
                'IBC-HC': dict(chain_list_file="data/steel/factories/IBF_factory-CCS.xlsx",
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
                'DRI-0C': dict(chain_list_file="data/steel/factories/DRI_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF-0C",
                                        scenario='MID-0B'),
                'DRI-LC': dict(chain_list_file="data/steel/factories/DRI_factory-CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF-LC",
                                        scenario='MID-0B'),
                'DRI-HC': dict(chain_list_file="data/steel/factories/DRI_factory-max CCS.xlsx",
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
ibf_subdirs = ['No Biomass/BBF', 'No Biomass/TGR', 'No Biomass/HIS', 'Low Biomass/BBF', 'Low Biomass/TGR', 'Low Biomass/HIS', 'High Biomass/BBF', 'High Biomass/TGR', 'High Biomass/HIS']
ibf_elec_scenarios = ['BBF-0B', 'TGR-0B', 'HIS-0B', 'BBF-LB', 'TGR-LB', 'HIS-LB', 'BBF-HB', 'TGR-HB', 'HIS-HB']

for i in range(len(ibf_elec_scenarios)):

    dat.outdir = f'{outdir}/Electricity/{ibf_subdirs[i]}'
    com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
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

dri_subdirs = ['No Biomass/MID', 'No Biomass/ULC', 'Low Biomass/MID', 'Low Biomass/ULC', 'High Biomass/MID', 'High Biomass/ULC',]
dri_elec_scenarios = ['MID-0B', 'ULC-0B', 'MID-LB', 'ULC-LB', 'MID-HB', 'ULC-HB',]
for i in range(len(dri_elec_scenarios)):
    dat.outdir = f'{outdir}/Electricity/{dri_subdirs[i]}'
    com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-LC', 'DRI-HC'], 
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
                                

# HIsarna energy use
his_subdirs = ['No Biomass', 'Low Biomass', 'High Biomass']
his_fuel_scenarios = ['HIS-0B', 'HIS-LB','HIS-HB']
for i in range(len(his_fuel_scenarios)):
    dat.outdir = f'{outdir}/HIsarna energy/{his_subdirs[i]}'
    com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
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

#BIOMASS Emissions
ibf_subdirs = ['Low Biomass/BBF', 'Low Biomass/TGR', 'Low Biomass/HIS', 'High Biomass/BBF', 'High Biomass/TGR', 'High Biomass/HIS']
ibf_elec_scenarios = ['BBF-LB', 'TGR-LB', 'HIS-LB', 'BBF-HB', 'TGR-HB', 'HIS-HB',]

for i in range(len(ibf_elec_scenarios)):

    dat.outdir = f'{outdir}/biomass/{ibf_subdirs[i]}'
    com.test_factory_sensitivity(factory_dict=BF_factory_dict,
                                scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC',], 
                                scenario=ibf_elec_scenarios[i],
                                chain_name='steel', 
                                unit_name='simple_BF', 
                                variable='secondary biofuel type', 
                                variable_options=['charcoal - IPCC', 'charcoal-low upstream', 'charcoal-high upstream'],
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
                                outdir=f'{outdir}/biomass/{ibf_subdirs[i]}')


dri_subdirs = ['Low Biomass/MID', 'Low Biomass/ULC', 'High Biomass/MID', 'High Biomass/ULC',]
dri_elec_scenarios = ['MID-LB', 'ULC-LB', 'MID-HB', 'ULC-HB',]
for i in range(len(dri_elec_scenarios)):
    dat.outdir = f'{outdir}/biomass/{dri_subdirs[i]}'
    com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-LC', 'DRI-HC'], 
                                scenario=dri_elec_scenarios[i],
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
                                outdir=f'{outdir}/biomass/{dri_subdirs[i]}')

#Syngas type
dri_subdirs = ['Low Biomass/MID', 'Low Biomass/ULC', 'High Biomass/MID', 'High Biomass/ULC',]
dri_elec_scenarios = ['MID-LB', 'ULC-LB', 'MID-HB', 'ULC-HB',]
for i in range(len(dri_elec_scenarios)):
    dat.outdir = f'{outdir}/syngasLHV/{dri_subdirs[i]}'
    com.test_factory_sensitivity(factory_dict=DRI_factory_dict,
                                scenario_factories=['DRI-0C', 'DRI-LC', 'DRI-HC'], 
                                scenario=dri_elec_scenarios[i],
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