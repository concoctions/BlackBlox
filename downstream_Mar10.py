"""TESTING FILE
"""

import compute as com
import dataconfig as dat
import io_functions as iof
from datetime import datetime
from collections import defaultdict
import importlib

# ==============================================================================
#  USER INPUT SECTION  =========================================================


################################################################################
# SPECIFY METADATA
################################################################################

dat.user_data = {"name": "S.E. Tanzer",
                 "affiliation": "TU Delft",
                 "project": f"Steel tests - {datetime.now().strftime('%d %B %Y')}",
}

dat.default_units = {'mass': 't', 
                     'energy':'GJ',
}


write_to_console = True
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
# SPECIFY TEST DATA
###############################################################################

qty = (1/0.972864) # hot rolled coil out

factory_dict = {
                'IBF-finish': dict(chain_list_file='data/steel/factories/finishing_IBF.xlsx',
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-0C",
                                        scenario='BBF-0B'),
                'DRI-finish': dict(chain_list_file='data/steel/factories/finishing_DRI.xlsx',
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name='DRI-0C',
                                        scenario='MID-0B'),
                'clinker-finish': dict(chain_list_file='data/cement/factories/finishing_clinker.xlsx',
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name='clinker-0C',
                                        scenario='CLK-0B'),
}

com.test_factory_scenarios(factory_dict=factory_dict,
                            scenario_factories=['IBF-finish'], 
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            scenario_list=['BBF-0B'], 
                            upstream_outflows=['CO2'], 
                            upstream_inflows=['CO2 removed'],
                            downstream_inflows=['CO2 removed'],
                            aggregate_flows=['CO2', 'CO2__fossil', 'CO2__bio', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}',
                            filename='_down-BF',
                            productname='iron')

qty = 1.0 # clinker in

com.test_factory_scenarios(factory_dict=factory_dict,
                            scenario_factories=['clinker-finish'], 
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            scenario_list=['CLK-0B'], 
                            upstream_outflows=['CO2'], 
                            upstream_inflows=['CO2 removed'],
                            downstream_inflows=['CO2 removed'],
                            aggregate_flows=['CO2', 'CO2__fossil', 'CO2__bio', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}',
                            filename='_down-CLK',
                            productname='clinker')

qty = (1/0.97308) # hot rolled coil out

com.test_factory_scenarios(factory_dict=factory_dict,
                            scenario_factories=['DRI-finish'], 
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            scenario_list=['MID-0B'], 
                            upstream_outflows=['CO2'], 
                            upstream_inflows=['CO2 removed'],
                            downstream_inflows=['CO2 removed'],
                            aggregate_flows=['CO2', 'CO2__fossil', 'CO2__bio', 'CO2 removed', 'CO2__upstream', 'stored CO2'],
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}',
                            filename='_down-DRI',
                            productname='iron')