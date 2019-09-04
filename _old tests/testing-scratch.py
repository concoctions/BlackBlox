"""TESTING FILE
"""
import compute as com
import dataconfig as dat
from datetime import datetime
from collections import defaultdict
import pandas as pan
import io_functions as iof
import unitprocess as uni
import processchain as cha
import factory as fac
import industry as ind

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



################################################################################
# SPECIFY OUTPUT
################################################################################


# for all tests
write_to_console = False
today = f'{datetime.now().strftime("%b%d")}/{datetime.now().strftime("%H%M")}'
dat.outdir = f'output/test_{today}'

# for chain, factory, and industry tests
view_diagrams = False
save_diagrams = True

# for factory and industry tests
write_to_xls = True

# for multi-scenario factory tests
individual_xls = True


###############################################################################
# SPECIFY TEST DATA
###############################################################################

qty = 1.0


factory_dict = {
                'Simplified Steel': dict(chain_list_file="data/steel/steel_simplified_factory-birat.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF Steel Mill",
                                        scenario='default'),
}


built_factories = com.build_factories(factory_dict)

BF = built_factories['Simplified Steel'].chain_dict['steel']['chain'].process_dict['simple_BF']

for i in [0.25, 0.5, 0.75, 1.0]:
    BF.var_df.loc['default', 'primary fuel demand'] = i

    u_in, u_out = BF.balance(1, scenario='default')

    flows = iof.make_df(dict(inflows=u_in, outflows=u_out))
    flows = iof.mass_energy_df(flows)
    print(flows)