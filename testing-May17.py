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

pause_between_tests = False

# for all tests
write_to_console = True
outdir = f'output/test_{datetime.now().strftime("%b%d")}/{datetime.now().strftime("%H%M")}'

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

# TEST LEVEL OF DETAIL FACTORIES

LoD_factory_dict = {
                'Detailed Steel-Crude': dict(chain_list_file="data/steel/IEAGHG_factory-crudesteel.xlsx",
                                            chain_list_sheet='IEAGHG chains', 
                                            connections_sheet='IEAGHG connections', 
                                                    name="BF Steel (IEAGHG)",
                                                    scenario='ieaghg-reference'),
                'Birat Steel': dict(chain_list_file="data/steel/birat_factories.xlsx",
                                        chain_list_sheet='base chains', 
                                        connections_sheet='base connections', 
                                        name="BF Steel (IEAGHG-Birat)",
                                        scenario='ieaghg-reference'),
                'Simplified Steel-IEAGHG': dict(chain_list_file="data/steel/steel_simplified_factory-ieaghg.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF Steel Mill",
                                        scenario='ieaghg-reference'),
}

com.test_factories(LoD_factory_dict,
                qty=qty,
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams)


# COMPARE REGIONS BASE TECH

base_factory_dict= {
            'Simplified Steel': dict(chain_list_file="data/steel/steel_simplified_factory.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='EU-BF-base'),
}


base_factory_list = [
                      'Simplified Steel',
                      ]

test_factory_scenarios(factory_dict,
                        scenario_factories, 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=[scenario], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams):

# COMPARE BECCS - BASE TECH - EU

# COMPARE BECCS - BASE TECH - CHINA

# EVOLVE INDUSTRY - EU

# EVOLVE INDUSTRY - CHINA

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
                'Detailed Steel-Crude': dict(chain_list_file="data/steel/IEAGHG_factory-crudesteel.xlsx",
                                        chain_list_sheet='IEAGHG chains', 
                                        connections_sheet='IEAGHG connections', 
                                        name="BF Steel (IEAGHG)",
                                        scenario='ieaghg-reference'),
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
                'Birat Steel': dict(chain_list_file="data/steel/birat_factories.xlsx",
                                        chain_list_sheet='base chains', 
                                        connections_sheet='base connections', 
                                        name="BF Steel (IEAGHG-Birat)",
                                        scenario='ieaghg-reference'),
                'Simplified Steel-IEAGHG': dict(chain_list_file="data/steel/steel_simplified_factory-ieaghg.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF Steel Mill",
                                        scenario='ieaghg-reference'),
                'Simplified Steel': dict(chain_list_file="data/steel/steel_simplified_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF Steel Mill",
                                        scenario='EU-BF-base'),
                'Simplified Steel-CCS': dict(chain_list_file="data/steel/steel_simplified_factory-ccs.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-Steel Mill-CCS",
                                        scenario='test'),
                'Simplified Steel-CCS-BF': dict(chain_list_file="data/steel/steel_simplified_factory-ccs-bfonly.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-Steel Mill-CCS_BF",
                                        scenario='test'),
                'Simplified Steel-CCS-BFC': dict(chain_list_file="data/steel/steel_simplified_factory-ccs-bfcoke.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-Steel Mill-CCS_BF-CO",
                                        scenario='test'),
                # 'fuel test': dict(chain_list_file="data/steel/fuel_test_factory.xlsx",
                #                         chain_list_sheet='chains', 
                #                         connections_sheet='connections', 
                #                         name="upstream fuel test",
                #                         scenario='test'),
                }


# SCENARIOS TO BE TESTED - comment out unwanted entries
scenario_factories = [
                      'Simplified Steel',
                      'Simplified Steel-CCS',
                      'Simplified Steel-CCS-BF',
                      'Simplified Steel-CCS-BFC',
                    #   'fuel test'
                      ]

scenario_list = [
                # 'test',
                # 'test-charcoal primary',
                # 'test-woodchip primary',
                # 'test-charcoal both',
                # 'test-woodchip both',
                # 'test-charcoal woodchip',
                # 'test-woodchip charcoal',
                # 'China-BF-base',
                'EU-BF-base',
                # 'Japan-BF-base',
                # 'Russia-BF-base',
                # 'USA-BF-base',
                # 'India-BF-base',
                'EU-BF-I',
                'EU-BF-C',
                'EU-BF-M',
                'EU-BF-F',
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
                #  'steel-EUROFER': dict(factory_list_file='data/steel/steel_Eurofer_industry.xlsx',
                #                        factory_list_sheet='Factory List', 
                #                        name='EUROFER Steel',
                #                        steps=[1990, 2010, 2030, 2050],
                #                        step_sheets=['1990', '2010', '2030', '2050'], 
                #                        write_to_xls=write_to_xls, 
                #                        graph_outflows=['CO2__emitted', 'steel'],
                #                        graph_inflows=False),
                #  'steel-EUROFER-CCS': dict(factory_list_file='data/steel/steel_Eurofer_industry-CCS.xlsx',
                #                        factory_list_sheet='Factory List', 
                #                        name='EUROFER Steel CCS',
                #                        steps=[1990, 2010, 2030, 2050],
                #                        step_sheets=['1990', '2010', '2030', '2050'], 
                #                        write_to_xls=write_to_xls, 
                #                        graph_outflows=['CO2__emitted', 'steel'],
                #                        graph_inflows=False),
                #  'steel-EUROFER-noCCS': dict(factory_list_file='data/steel/steel_Eurofer_industry-noCCS.xlsx',
                #                        factory_list_sheet='Factory List', 
                #                        name='EUROFER Steel no CCS',
                #                        steps=[1990, 2010, 2030, 2050],
                #                        step_sheets=['1990', '2010', '2030', '2050'], 
                #                        write_to_xls=write_to_xls, 
                #                        graph_outflows=['CO2__emitted', 'steel'],
                #                        graph_inflows=False),
                 'steel-EU28-PBC': dict(factory_list_file='data/steel/steel_industry_EU28.xlsx',
                                       factory_list_sheet='Factory List', 
                                       name='EUROFER Steel no CCS',
                                       steps=[1990, 2010, 2015, 2030, 2050],
                                       step_sheets=['1990', '2010', '2015', '2030', '2050'], 
                                       write_to_xls=com.write_to_xls, 
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
