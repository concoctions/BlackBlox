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


################################################################################
# SPECIFY TESTS TO RUN 
################################################################################

test_units = True
test_chains = False
test_factories = False
test_factory_scenarios = True
test_industries = False
test_industry_evolve = False
compare_evolved_industres = False


################################################################################
# SPECIFY OUTPUT
################################################################################

pause_between_tests = False

# for all tests
write_to_console = True
dat.outdir = f'output/test_{datetime.now().strftime("%b%d")}/{datetime.now().strftime("%H%M")}'

# for chain, factory, and industry tests
view_diagrams = False
save_diagrams = False

# for factory and industry tests
write_to_xls = True

# for multi-scenario factory tests
individual_xls = True


###############################################################################
# SPECIFY TEST DATA
###############################################################################

qty = 1.0


#-------------------------------------------------------------------------------
# UNIT PROCESSES
#-------------------------------------------------------------------------------

scenario = 'default'

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
            # 'simple_coke',
            # 'simple_lime',
            # 'simple_pellets',
            # 'simple_sinter',
            # 'simple_BF',
            # 'simple_BOF',
            # 'simple_oxygen',
            # 'simple_power',
            # 'simple_fuel',
            # 'simple_CO2capture',
            # 'simple_CO2storage'
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
                # 'IEAGHG Ref': dict(chain_list_file="data/steel/IEAGHG_factories.xlsx",
                #                         chain_list_sheet='IEAGHG chains', 
                #                         connections_sheet='IEAGHG connections', 
                #                         name="BF Steel (IEAGHG)",
                #                         scenario='ieaghg-reference'),
                # 'Detailed Steel-Crude': dict(chain_list_file="data/steel/IEAGHG_factory-crudesteel.xlsx",
                #                         chain_list_sheet='IEAGHG chains', 
                #                         connections_sheet='IEAGHG connections', 
                #                         name="BF Steel (IEAGHG)",
                #                         scenario='ieaghg-reference'),
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
                # 'Birat CCS_LC': dict(chain_list_file="data/steel/birat_factories.xlsx",
                #                         chain_list_sheet='CCS-LC chains', 
                #                         connections_sheet='CCS-LC connect', 
                #                         name="BF-TGR-CCS Steel with Upstream",
                #                         scenario='birat-tgr-63vpsa-100bio'),
                # 'BF-EAF BB': dict(chain_list_file="data/steel/bb_steel_factories.xlsx",
                #                         chain_list_sheet='bf-eaf chains', 
                #                         connections_sheet='bf-eaf connections', 
                #                         name="BF-EAF Steel Industry",
                # #                         scenario='EUROFER 2010'),
                # 'Birat Steel': dict(chain_list_file="data/steel/birat_factories.xlsx",
                #                         chain_list_sheet='base chains', 
                #                         connections_sheet='base connections', 
                #                         name="BF Steel (IEAGHG-Birat)",
                #                         scenario='ieaghg-reference'),
                # 'Simplified Steel': dict(chain_list_file="data/steel/steel_simplified_factory.xlsx",
                #                         chain_list_sheet='chains', 
                #                         connections_sheet='connections', 
                #                         name="BF-BOF Steel Mill",
                #                         scenario='EU-BF-base'),
                'Simplified Steel-CCS': dict(chain_list_file="data/steel/steel_simplified_factory-ccs.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF Steel Mill with CCS",
                                        scenario='test'),
                'fuel test': dict(chain_list_file="data/steel/fuel_test_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="upstream fuel test",
                                        scenario='test'),
                }


# SCENARIOS TO BE TESTED - comment out unwanted entries
scenario_factories = [
                      # 'Simplified Steel',
                      # 'Simplified Steel-CCS',
                      'fuel test'
                      ]

scenario_list = [
                'test',
                'test-charcoal primary',
                'test-woodchip primary',
                'test-charcoal both',
                'test-woodchip both',
                'test-charcoal woodchip',
                'test-woodchip charcoal',
                # 'China-BF-base',
                # 'EU-BF-base',
                # 'Japan-BF-base',
                # 'Russia-BF-base',
                # 'USA-BF-base',
                #  'birat-base', 
                #  'birat-tgr-63vpsa',
                #  'birat-tgr-63vpsa-50bio',
                #  'birat-tgr-63vpsa-100bio',
                #  'birat-tgr-100vpsa-100bio',
                ]

# PRODUCT TO BE TESTED - in run scenarios
scenario_product = False
scenario_unit = False
scenario_io = False

#-------------------------------------------------------------------------------
# INDUSTRIES
#-------------------------------------------------------------------------------

industry_dict = {
                 'steel-EUROFER': dict(factory_list_file='data/steel/steel_Eurofer_industry.xlsx',
                                       factory_list_sheet='Factory List', 
                                       name='EUROFER Steel',
                                       steps=[1990, 2010, 2030, 2050],
                                       step_sheets=['1990', '2010', '2030', '2050'], 
                                       write_to_xls=write_to_xls, 
                                       graph_outflows=['CO2__emitted', 'steel'],
                                       graph_inflows=False),
                 'steel-EUROFER-CCS': dict(factory_list_file='data/steel/steel_Eurofer_industry-CCS.xlsx',
                                       factory_list_sheet='Factory List', 
                                       name='EUROFER Steel CCS',
                                       steps=[1990, 2010, 2030, 2050],
                                       step_sheets=['1990', '2010', '2030', '2050'], 
                                       write_to_xls=write_to_xls, 
                                       graph_outflows=['CO2__emitted', 'steel'],
                                       graph_inflows=False),
                 'steel-EUROFER-noCCS': dict(factory_list_file='data/steel/steel_Eurofer_industry-noCCS.xlsx',
                                       factory_list_sheet='Factory List', 
                                       name='EUROFER Steel no CCS',
                                       steps=[1990, 2010, 2030, 2050],
                                       step_sheets=['1990', '2010', '2030', '2050'], 
                                       write_to_xls=write_to_xls, 
                                       graph_outflows=['CO2__emitted', 'steel'],
                                       graph_inflows=False),
}

compare_industry_name = 'EUROFER'
compare_steps = [1990, 2010, 2030, 2050]
compare_step_sheets = ['1990', '2010', '2030', '2050']
compare_outflows = ['CO2__emitted', 'steel']
compare_inflows = False

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

        if pause_between_tests is True:
            dummy_continue = input("Press any key to continue")


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
        
        if pause_between_tests is True:
            dummy_continue = input("Press any key to continue")


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
    print(f'\nbalancing factories on {qty} of main product... \n')
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
            print(f"\n FACTORY: Full results available in {dat.outdir} directory.")

        if pause_between_tests is True:
            dummy_continue = input("Press any key to continue")

if test_factory_scenarios is True:
    print(f'\ncomparing factory outputs for {scenario_list}. for {qty} of product... \n')

    for f in scenario_factories:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory - multiscenario")

        inflows, outflows = factory.run_scenarios(scenario_list=scenario_list, 
                                                  product_qty=qty, 
                                                  product=scenario_product, 
                                                  product_unit=scenario_unit, 
                                                  product_io=scenario_io,
                                                  write_to_xls=individual_xls)

        if write_to_console is True:
            print(f"\n{factory.name} inflows")
            print(inflows)

            print(f"\n{factory.name} outflows")
            print(outflows)

        print(f"\n FACTORY (multi-scenario): Full results available in {dat.outdir} directory.")

        if pause_between_tests is True:
            dummy_continue = input("Press any key to continue")

#------------------------------------------------------------------------------
# INDUSTRY TEST

built_industries = dict()
if test_industries is True or test_industry_evolve is True:
    for i in industry_dict:
        industry = ind.Industry(**industry_dict[i])
        built_industries[i] = industry

if test_industries is True:
    pass

if test_industry_evolve is True:
    ind_annual = iof.nested_dicts(4) #[i_o][industry name][substance][time step]
    ind_cumulative = iof.nested_dicts(3) #[i_o][industry name][substance]
    for i in industry_dict:
        industry = built_industries[i]
        if compare_evolved_industres is True and compare_steps is not False:
            industry_dict[i]['steps'] = compare_steps
        if compare_evolved_industres is True and compare_step_sheets is not False:
            industry_dict[i]['step sheets'] = compare_step_sheets
        annual, cumulative = industry.evolve_multistep(**industry_dict[i])

        ind_annual['i'][i] = annual['inflows']['industry totals']
        ind_annual['o'][i] = annual['outflows']['industry totals']

        ind_cumulative['i'][i] = cumulative['inflows']['industry totals']
        ind_cumulative['o'][i] = cumulative['outflows']['industry totals']

        if pause_between_tests is True:
            dummy_continue = input("Press any key to continue")
    
    if compare_evolved_industres is True and compare_steps is not False:

        filename = (f'i_{compare_industry_name}_comparison_{compare_steps[0]}-{compare_steps[-1]}'
                    f'_{datetime.now().strftime("%Y-%m-%d_%H%M")}')

        cumulative_infows_df = iof.make_df(ind_cumulative['i'], drop_zero=True, metaprefix=None)
        cumulative_infows_df = iof.mass_energy_df(cumulative_infows_df, aggregate_consumed=True)
        cumulative_outflows_df = iof.make_df(ind_cumulative['o'], drop_zero=True, metaprefix=None)
        cumulative_outflows_df = iof.mass_energy_df(cumulative_outflows_df, aggregate_consumed=True)

        meta_df = iof.metadata_df(user=dat.user_data, name=f'{compare_industry_name}_comparison', 
                        level="Industry", scenario="n/a", product="n/a",
                        product_qty="n/a", energy_flows=dat.energy_flows)

        df_list = [meta_df, cumulative_infows_df, cumulative_outflows_df]
        sheet_list = ["meta", "inflows (cumulative)", "outflows (cumulative)"]

        df_dict = iof.nested_dicts(2)

        for flow in ind_annual:
            for factory in ind_annual[flow]:
                df = iof.make_df(ind_annual[flow][factory], drop_zero=False, sort=True, metaprefix=None)
                sheet_name = f'{factory} {flow}'
                df_dict[flow[0]][factory] = df
                df_list.append(df)
                sheet_list.append(sheet_name)
        
        iof.write_to_excel(df_list, sheet_list=sheet_list, filedir=dat.outdir, filename=filename)

        if type(compare_outflows) is list:
            for flow in compare_outflows:
                iof.plot_annual_flows(df_dict['o'], flow, dat.outdir, file_id=f"_{compare_industry_name}-comparison")

        if type(compare_inflows) is list:
            for flow in compare_outflows:
                iof.plot_annual_flows(df_dict['i'], flow, dat.outdir, file_id=f"_{compare_industry_name}-comparison")

    
        print(f"\n INDUSTRY COMPARISON - Full results available in {dat.outdir} directory.")

        if pause_between_tests is True:
            dummy_continue = input("Press any key to continue")