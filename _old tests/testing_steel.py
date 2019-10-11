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
write_to_console = True
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

# chain_dict = {
#               'steel': dict(name='steel',
#                             chain_data="data/steel/factories/IBF_factory-scrap.xlsx",
#                             xls_sheet='steel'),
#               }


# com.test_chains(chain_dict=chain_dict, 
#                 qty=1.0, 
#                 scenario="BBF-0B", 
#                 write_to_console=True, 
#                 view_diagrams=view_diagrams,
#                 save_diagrams=save_diagrams)

factory_dict = {
                'IBC-0C': dict(chain_list_file="data/steel/factories/IBF_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-0C",
                                        scenario='BBF-0B'),
                'IBC-HC': dict(chain_list_file="data/steel/factories/IBF_factory-CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF-HC",
                                        scenario='BBF-0B'),
}


dat.outdir = f'{outdir}'

com.test_factory_scenarios(factory_dict=factory_dict,
                scenario_factories=['IBC-0C', 'IBC-HC'],
                scenario_list=['BBF-0B', 'HIS-HB'], 
                scenario_product=False,
                scenario_unit=False,
                scenario_io=False,
                qty=qty, 
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=outdir,
                upstream_outflows=['CO2'], 
                upstream_inflows=['CO2 removed'],
                aggregate_flows=['CO2', 'CO2 removed', 'CO2__upstream'])
