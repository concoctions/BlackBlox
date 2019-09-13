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
outdir = f'output/syngas_{today}'

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

factory_dict = {
                'syngas': dict(chain_list_file="data/steel/factories/syngas_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name='syngas',
                                        scenario='syngas_only'),
}



dat.outdir = f'{outdir}'

com.test_factory_scenarios(factory_dict=factory_dict,
                scenario_factories=['syngas'],
                scenario_list=['syngas_ecoinvent', 'syngas_only', 'syngas_PNNL'], 
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

