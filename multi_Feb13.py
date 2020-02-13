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
save_diagrams = False

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

factory_dict = {
                'clinker-0C': dict(chain_list_file='data/cement/factories/clinker_factory-0C.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='clinker-0C',
                                    scenario='Schakel2018-0B'),
                'clinker-HC': dict(chain_list_file='data/cement/factories/clinker_factory-HC.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='clinker-HC',
                                    scenario='Schakel2018-0B'),
                'clinker-CLC': dict(chain_list_file='data/cement/factories/clinker_factory-CLC.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='clinker-CLC',
                                    scenario='Schakel2018-0B'),
}


com.test_factory_scenarios(factory_dict=factory_dict,
                        scenario_factories=['clinker-0C', 'clinker-HC', 'clinker-CLC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['Schakel2018-0B', 'Schakel2018-HB'], 
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
                'IBC-0C': dict(chain_list_file="data/steel/factories/iron_IBF_factory-0C.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-0C",
                                        scenario='BBF-0B'),
                'IBC-HC': dict(chain_list_file="data/steel/factories/iron_IBF_factory-HC.xlsx",
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
                            scenario_factories=['IBC-0C', 'IBC-HC'], 
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