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
# COMPARE BF BECCS SCENARIOS, BY TECHNOLOGY



BF_factory_dict = {
                'IBC-0C': dict(chain_list_file="data/steel/factories/IBF_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF wo CCS",
                                        scenario='BBF-0B'),
                'IBC-LC': dict(chain_list_file="data/steel/factories/IBF-factory-BFG CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF w BFG-only CCS",
                                        scenario='BBF-0B'),
                'IBC-HC': dict(chain_list_file="data/steel/factories/IBF_factory-CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF w CCS",
                                        scenario='BBF-0B'),
}

dat.outdir = f'{outdir}/BBF'
com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-0B', 'BBF-LB', 'BBF-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BBF')


dat.outdir = f'{outdir}/TGR/'
com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['TGR-0B', 'TGR-LB', 'TGR-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/TGR')

dat.outdir = f'{outdir}/HIS/'
com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['HIS-0B', 'HIS-LB', 'HIS-HB',], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/HIS')

# ###############################################################################
# # COMPARE BF TECHNOLOGIES, BY BECCS SCENARIO

dat.outdir = f'{outdir}/BF-multitech/No Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-0B', 'TGR-0B', 'HIS-0B'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BF-multitech/No Biomass')


dat.outdir = f'{outdir}/BF-multitech/Low Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-LB', 'TGR-LB', 'HIS-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BF-multitech/Low Biomass')


dat.outdir = f'{outdir}/BF-multitech/High Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-HB', 'TGR-HB', 'HIS-HB',], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BF-multitech/High Biomass')




###############################################################################
# COMPARE BECCS SCENARIOS, BY DRI TECHNOLOGY

DRI_factory_dict = {
                'DRI-0C': dict(chain_list_file="data/steel/factories/DRI_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF wo CCS",
                                        scenario='MID-0B'),
                'DRI-LC': dict(chain_list_file="data/steel/factories/DRI_factory-CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF w CCS",
                                        scenario='MID-0B'),
                'DRI-HC': dict(chain_list_file="data/steel/factories/DRI_factory-max CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF w total CCS",
                                        scenario='MID-0B'),
}

dat.outdir = f'{outdir}/MID'
com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['MID-0B', 'MID-LB', 'MID-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/MID')


dat.outdir = f'{outdir}/ULC/'
com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['ULC-0B', 'ULC-LB', 'ULC-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/ULC')

###############################################################################
# COMPARE DRI TECHNOLOGIES, BY BECCS SCENARIOS

dat.outdir = f'{outdir}/DRI-multitech/No Biomass'

com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['MID-0B', 'ULC-0B'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/DRI-multitech/No Biomass')


dat.outdir = f'{outdir}/DRI-multitech/Low Biomass'

com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['MID-LB', 'ULC-LB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/DRI-multitech/Low Biomass')


dat.outdir = f'{outdir}/DRI-multitech/High Biomass'

com.test_factory_scenarios(factory_dict=DRI_factory_dict,
                        scenario_factories=['DRI-0C','DRI-LC', 'DRI-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['MID-HB', 'ULC-HB'], 
                        upstream_outflows=['CO2'], 
                        upstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/DRI-multitech/High Biomass')

# ###############################################################################
# # SENSITIVITY ANALYSES

# # electricity mix
dat.outdir = f'{outdir}/Electricity'

electricity_factory_dict= {
                'IBC-0C': dict(chain_list_file="data/steel/factories/IBF_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF wo CCS",
                                        scenario='BBF-0B'),
                'IBC-LC': dict(chain_list_file="data/steel/factories/IBF-factory-BFG CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF w BFG-only CCS",
                                        scenario='BBF-0B'),
                'IBC-HC': dict(chain_list_file="data/steel/factories/IBF_factory-CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF w CCS",
                                        scenario='BBF-0B'),
}

com.test_factory_sensitivity(factory_dict=electricity_factory_dict,
                            scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                            scenario='BBF-0B',
                            chain_name='power', 
                            unit_name='simple_power', 
                            variable='fueltype', 
                            variable_options=['natural gas - IPCC', 'electricity PROXY - EU 2016', 'electricity PROXY - CN 2016', 'electricity PROXY - decarbonized'],
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            upstream_outflows=['CO2'], 
                            upstream_inflows=['CO2 removed'],
                            aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'],
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}/Electricity')