"""TESTING FILE
"""

import dataconfig as dat
from datetime import datetime

# ==============================================================================
#  USER INPUT SECTION  =========================================================


################################################################################
# SPECIFY METADATA
################################################################################

dat.user_data = {"name": "S.E. Tanzer",
                 "affiliation": "TU Delft",
                 "project": f"Steel tests - {datetime.now().strftime('%d %B %Y')}",
}

dat.default_units = {'mass': 'tonnes', 
                     'energy':'GJ',
}


################################################################################
# SPECIFY TESTS TO RUN 
################################################################################

test_units = False
test_chains = False
test_factories = True
test_factory_scenarios = False
# test_industries = False
# test_industry_evolve = False


################################################################################
# SPECIFY OUTPUT
################################################################################

# for all tests
write_to_console = True
dat.outdir = "output/test"

# for chain, factory, and industry tests
view_diagrams = False
save_diagrams = True

# for factory and industry tests
write_to_xls = False


###############################################################################
# SPECIFY TEST DATA
###############################################################################

qty = 1.0


#-------------------------------------------------------------------------------
# UNIT PROCESSES
#-------------------------------------------------------------------------------

scenario = 'birat-tgr-63vpsa-50bio'

# UNITS TO BE TESTED - comment out unwanted entries
unit_list = [
            # 'IEAGHGsteel_coke_oven',
            # 'IEAGHGsteel_sinter_plant',
            # 'IEAGHGsteel_blast_furnace', 
            # 'IEAGHGsteel_BOF',
            # 'IEAGHGsteel_ladle',
            # 'IEAGHGsteel_forming',
            # 'aux_lime kiln',
            # 'aux_air separation',
            # 'electricity_1step',
            # 'heat_collector',
            # 'birat_steel_plant',
            # 'bb_steel_bf',
            # 'bb_steel_eaf',
            # 'bb_steel_bf-eaf',
            # 'CO2_capture',
            # 'CO2_compression',
            # 'CO2_capture-compression',
            # 'bb_fuel_upstream',
            # 'bb_biofuel_upstream',
            # 'bb_CO2_storage',
             ]


#-------------------------------------------------------------------------------
# PROCESS CHAINS
#-------------------------------------------------------------------------------

# CHAINS TO BE TESTED - comment out unwanted entries
chain_dict = {
              'steel': dict(name='steel',
                            chain_data="data/steel/steel_factories.xlsx",
                            xls_sheet='steel chain'),
}


#-------------------------------------------------------------------------------
# FACTORIES
#-------------------------------------------------------------------------------

# FACTORIES TO BE TESTED - comment out unwanted entries
factory_dict = {
                # 'IEAGHG steel': dict(chain_list_file="data/steel/IEAGHG_factories.xlsx",
                #                         chain_list_sheet='IEAGHG chains', 
                #                         connections_sheet='IEAGHG connections', 
                #                         name="IEAGHG Steel Plant",
                #                         scenario='IEAGHG 2013'),
                # 'Birat steel base': dict(chain_list_file="data/steel/birat_factories.xlsx",
                #                         chain_list_sheet='base chains', 
                #                         connections_sheet='base connections', 
                #                         name="BF Steel Plant",
                #                         scenario='birat-base'),
                # 'Birat CCS': dict(chain_list_file="data/steel/birat_factories.xlsx",
                #                         chain_list_sheet='TGR-CCS chains', 
                #                         connections_sheet='TGR-CCS connect', 
                #                         name="BF-TGR-CCS Steel Plant",
                #                         scenario='birat-tgr-63vpsa'),
                'Birat CCS_LC': dict(chain_list_file="data/steel/birat_factories.xlsx",
                                        chain_list_sheet='CCS-LC chains', 
                                        connections_sheet='CCS-LC connect', 
                                        name="BF-TGR-CCS Steel with Upstream",
                                        scenario='birat-tgr-63vpsa-100bio'),
}

# SCENARIOS TO BE TESTED - comment out unwanted entries
scenario_list = [
                 'birat-base', 
                 'birat-tgr-63vpsa',
                 'birat-tgr-63vpsa-50bio',
                 'birat-tgr-63vpsa-100bio',
                 'birat-tgr-100vpsa-100bio',
]

# PRODUCT TO BE TESTED - in run scenarios
scenario_product = False
scenario_unit = False
scenario_io = False

#-------------------------------------------------------------------------------
# INDUSTRIES
#-------------------------------------------------------------------------------

# TO BE ADDED


#  END OF USER INPUT SECTION  ==================================================
# ==============================================================================


import pandas as pan
import io_functions as iof
import unitprocess as uni
import processchain as cha
import factory as fac


#------------------------------------------------------------------------------
# UNIT TESTS

if test_units is True:
    for unit_id in unit_list:
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


#------------------------------------------------------------------------------
# CHAIN TESTS

if test_chains is True:
    for c in chain_dict:
        chain = cha.ProductChain(**chain_dict[c])
        chain.build()
        print(f"\n{str.upper(chain.name)} chain")

        if view_diagrams is True or save_diagrams is True:
            chain.diagram(view=view_diagrams, save=save_diagrams)
        
        print(chain.process_dict)

        chain_inflows, chain_outflows, int_flows, int_rows = chain.balance(qty, scenario=scenario)

        if write_to_console is True:
            chain_inflows = iof.make_df(chain_inflows)
            chain_inflows = iof.mass_energy_df(chain_inflows)
            chain_outflows = iof.make_df(chain_outflows)
            chain_outflows = iof.mass_energy_df(chain_outflows)

            print(f'\nusing {scenario} values')
            print("\ninflows:\n", chain_inflows)
            print("\noutflows:\n", chain_outflows)

            print("\nintermediate flows:")
            for row in int_rows:
                print(row)


#------------------------------------------------------------------------------
# FACTORY TESTS

built_factories = dict()

if test_factories is True or test_factory_scenarios is True:
    for f in factory_dict:
        factory = fac.Factory(**factory_dict[f])
        factory.build()
        built_factories[f] = factory

        if view_diagrams is True or save_diagrams is True:
            factory.diagram(view=view_diagrams, save=save_diagrams)

if test_factories is True:
    print('\nbalancing factories on {qty} of main product... \n')
    for f in factory_dict:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory")
        
        inflows, outflows = factory.balance(product_qty = qty, 
                                            scenario=factory_dict[f]['scenario'], 
                                            write_to_xls=write_to_xls, 
                                            outdir=dat.outdir, 
                                            mass_energy=True, 
                                            energy_flows=dat.energy_flows)

        if write_to_console is True:
            print(f"\nusing {scenario} values and {qty} of {factory.main_product}:")
            totals = {'factory inflows': inflows, 'factory outflows': outflows}
            totals = pan.DataFrame(totals)
            totals = iof.mass_energy_df(totals)
            print(f"\n{factory.name} total inflows and outflows")
            print(totals)

        if write_to_xls is True:
            print(f"\n Full results available in {dat.outdir} directory.")


if test_factory_scenarios is True:
    print(f'\ncomparing factory outputs for {scenario_list}. for {qty} of product... \n')

    for f in factory_dict:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory - multiscenario")

        inflows, outflows = factory.run_scenarios(scenario_list=scenario_list, 
                                                  product_qty=qty, 
                                                  product=scenario_product, 
                                                  product_unit=scenario_unit, 
                                                  product_io=scenario_io,
                                                  write_to_xls=False)

        if write_to_console is True:
            print(f"\n{factory.name} inflows")
            print(inflows)

            print(f"\n{factory.name} outflows")
            print(outflows)

        print(f"\n Full results available in {dat.outdir} directory.")



#------------------------------------------------------------------------------
# INDUSTRY TEST

# TO BE ADDED