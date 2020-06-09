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
outdir = f'output/cement_{today}'

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

qty = 1.0/0.737 # standardized to 1 t clinker


###############################################################################

factory_dict = {
                'Cement-0C': dict(chain_list_file='data/cement/factories/cement_factory-0C.xlsx',
                                    chain_list_sheet='chains', 
                                    connections_sheet='connections', 
                                    name='cement-0C',
                                    scenario='CEMCAP-0C'),
}

dat.outdir = f'{outdir}'

com.test_factory_scenarios(factory_dict=factory_dict,
                        scenario_factories=['Cement-0C'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['CEMCAP-0C'], 
                        upstream_outflows=['CO2', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4'], 
                        upstream_inflows=['CO2 removed', 'factory CO2 removed'],
                        downstream_inflows=['CO2 removed'],
                        aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream', 'CH4 (CO2eq)', 'factory CO2', 'factory CH4''factory CO2 removed', 'stored CO2'],
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}')

