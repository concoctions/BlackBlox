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
outdir = f'output/charcoal_{today}'

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
# CHARCOAL PRODUCTION

# for scenario in ['ecoinvent GLO', 'Balis2013-HT', 'Balis2013-Sc3', 'Balis2013-Sc4', 'penisse2001-missouri', 'penisse2001-HT']:

#     com.test_units(['simple_charcoal'], 
#                 qty=1.0, 
#                 scenario=scenario, 
#                 write_to_console=True)

factory_dict = {
                'charcoal only': dict(chain_list_file="data/steel/factories/charcoal_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name='charcoal',
                                        scenario='default'),
                'IBF-0C': dict(chain_list_file="data/steel/factories/IBF_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-0C",
                                        scenario='BBF-0B'),
                'IBF-LC': dict(chain_list_file="data/steel/factories/IBF-factory-BFG CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-LC",
                                        scenario='BBF-0B'),
                'IBF-HC': dict(chain_list_file="data/steel/factories/IBF_factory-CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-HC",
                                        scenario='BBF-0B'),
}



dat.outdir = f'{outdir}'


# com.test_factory_scenarios(factory_dict=factory_dict,
#                 scenario_factories=['charcoal only'],
#                 scenario_list=['ecoinvent GLO', 'Balis2013-HT', 'Balis2013-Sc3', 'Balis2013-Sc4', 'penisse2001-missouri', 'penisse2001-HT'], 
#                 scenario_product=False,
#                 scenario_unit=False,
#                 scenario_io=False,
#                 qty=qty, 
#                 write_to_console=write_to_console, 
#                 write_to_xls=write_to_xls,
#                 view_diagrams=view_diagrams,
#                 save_diagrams=save_diagrams,
#                 outdir=outdir,
#                 upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
#                 upstream_inflows=['CO2 removed', 'factory CO2 removed'],
#                 aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4', 'factory CO2 removed', 'stored CO2'],)



com.test_factory_scenarios(factory_dict=factory_dict,
                scenario_factories=['IBF-0C', 'IBF-LC', 'IBF-HC'],
                scenario_list=['BBF-0B', 'BBF-LB', 'BBF-HB'], 
                scenario_product=False,
                scenario_unit=False,
                scenario_io=False,
                qty=qty, 
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=outdir,
                upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],)

com.test_factory_sensitivity(factory_dict=factory_dict,
                            scenario_factories=['IBF-HC'], 
                            scenario='BBF-HB',
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
                            outdir=outdir)