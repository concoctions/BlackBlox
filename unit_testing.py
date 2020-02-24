"""TESTING FILE
"""

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


# for all tests
write_to_console = True
dat.outdir = f'output/test_{datetime.now().strftime("%b%d")}/{datetime.now().strftime("%H%M")}'

###############################################################################
# SPECIFY TEST DATA
###############################################################################

qty = ( 1.0 )
pause_between_tests = True


#-------------------------------------------------------------------------------
# UNIT PROCESSES
#-------------------------------------------------------------------------------

scenario_list = ['IEAGHG',
                ]
unit_list = [
            'paper_chipping',
            'paper_pulping',
            'paper_bleaching',
            'paper_multifuel',
            'paper_blackliquor',
            'paper_caustic',
            'simple_lime',
            'simple_WWT',
            'simple_oxygen',
            'simple_power',
            ] 



#  END OF USER INPUT SECTION  ==================================================
# ==============================================================================


import pandas as pan
import io_functions as iof
import unitprocess as uni
import processchain as cha
import factory as fac
import industry as ind


#------------------------------------------------------------------------------
# UNIT TESTS

for unit_id in unit_list:
    for scenario in scenario_list:
        unit = uni.UnitProcess(unit_id)

        print(str.upper(unit.name))
        # print("\ninflows:", ', '.join(unit.inflows))
        # print("outflows:", ', '.join(unit.outflows))
        print("\nmass inflows:", ', '.join(unit.mass_inflows))
        print("mass outflows:", ', '.join(unit.mass_outflows))
        print("\nenergy inflows:", ', '.join(unit.energy_inflows))
        print("energy outflows:", ', '.join(unit.energy_outflows))
        u_in, u_out = unit.balance(qty, scenario=scenario)

        if write_to_console is True:
            print(f"using {scenario} values:")
            flows = iof.make_df(dict(inflows=u_in, outflows=u_out))
            flows = iof.mass_energy_df(flows)
            print(flows)

        if pause_between_tests is True and len(unit_list) > 1:
            dummy_continue = input("Press any key to continue ")