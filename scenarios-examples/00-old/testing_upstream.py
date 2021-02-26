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



###############################################################################
# TESTS
###############################################################################

qty = 1.0


import factory as fac
import pandas as pan

factory = fac.Factory(chain_list_file="data/steel/factories/IBF_factory.xlsx",
                        chain_list_sheet='chains', 
                        connections_sheet='connections', 
                        name="BF-BOF wo CCS",
                        scenario='BBF-0B')

inflows, outflows = factory.balance(product_qty = qty, 
                                    scenario='BBF-LB', 
                                    upstream_outflows=['CO2'],
                                    upstream_inflows=['CO2 removed'],
                                    aggregate_flows=['CO2', 'coal', 'O2'],
                                    write_to_xls=True,  
                                    mass_energy=True)

totals = {'factory inflows': inflows, 'factory outflows': outflows}
totals = pan.DataFrame(totals)
totals = iof.mass_energy_df(totals)

print(totals, "\n")