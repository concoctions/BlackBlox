"""TESTING FILE
"""
import compute as com
import dataconfig as dat
from datetime import datetime
from collections import defaultdict

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

com.test_factories(factory_dict,
                qty=qty,
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=False,
                save_diagrams=True,
                outdir=f'output/test_{today}')