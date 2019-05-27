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
                view_diagrams=False,
                save_diagrams=True,
                outdir=f'output/test_{today}/LevelOfDetail')


# COMPARE REGIONS BASE TECH
dat.outdir = f'output/test_{today}/RegionCompare'

base_factory_dict= {
            'Simplified Steel-GtG': dict(chain_list_file="data/steel/steel_simplified_factory-noupstream.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='EU-0B-2015',
                                outdir=f'output/test_{today}/RegionCompare'),
}


com.test_factory_scenarios(base_factory_dict,
                        ['Simplified Steel-GtG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-0B-2015', 'CH-0B-2015', 'JP-0B-2015', 'RU-0B-2015', 'US-0B-2015', 'IN-0B-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'output/test_{today}/RegionCompare')


# SCRAP RATIO SENSITIVITY

scrap_factory_dict= {
            'Simplified Steel-GtG': dict(chain_list_file="data/steel/steel_simplified_factory-noupstream.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='US-0B-2015',
                                outdir=f'output/test_{today}/ScrapRatio'),
}

built_factories = com.build_factories(scrap_factory_dict)

BOF = built_factories['Simplified Steel'].chain_dict['steel']['chain'].process_dict['simple_BOF']

for i in [0.0, 0.1, 0.2, 0.3, 0.4]:
    BOF.var_df.loc['US-0B-2015', 'scrap demand'] = i

    com.test_factories(scrap_factory_dict,
                        qty=qty,
                        write_to_console=True, 
                        write_to_xls=True,
                        view_diagrams=False,
                        save_diagrams=True,
                        outdir=f'output/test_{today}/ScrapRatio/{str(round(i*100))}percent')


# COMPARE BECCS - BASE TECH - EU

dat.outdir = f'output/test_{today}/BECCS-EU-Factory'

BECCS_factory_dict = {
                    'Steel': dict(chain_list_file="data/steel/steel_simplified_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF",
                                        scenario='EU-0B-2015'),
                'Steel_CCS-max': dict(chain_list_file="data/steel/steel_simplified_factory-ccs.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-max",
                                        scenario='EU-0B-2015'),
                'Steel_CCS-BF': dict(chain_list_file="data/steel/steel_simplified_factory-ccs-bfonly.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-BFG",
                                        scenario='EU-0B-2015'),
                'Steel_CCS-BF-COG': dict(chain_list_file="data/steel/steel_simplified_factory-ccs-bfcoke.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-BFGCOG",
                                        scenario='EU-0B-2015'),
}

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-0B-2015', 'EU-IB-2015', 'EU-CB-2015', 'EU-TB-2015', 'EU-FB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'output/test_{today}/BECCS-EU-Factory/2015')

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-0B-2050', 'EU-CB-2050'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'output/test_{today}/BECCS-EU-Factory/2050')

# COMPARE BECCS - BASE TECH - CHINA
dat.outdir = f'output/test_{today}/BECCS-CN-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['CH-0B-2015', 'CH-IB-2015', 'CH-CB-2015', 'CH-TB-2015', 'CH-FB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'output/test_{today}/BECCS-CN-Factory/2015')

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['CH-0B-2050', 'CH-CB-2050'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'output/test_{today}/BECCS-CN-Factory/2050')

# EVOLVE INDUSTRY - EUROFER
dat.outdir = f'output/test_{today}/EUROFER Industry'

EUROFER_industry_dict = {
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
                                       graph_inflows=False)
                                       }


com.test_industry_evolve(
                EUROFER_industry_dict,
                qty=qty, 
                compare_evolved_industres=True,
                compare_industry_name='EUROFER',
                compare_steps=[1990, 2010, 2030, 2050],
                compare_step_sheets=['1990', '2010', '2030', '2050'],
                compare_outflows=['CO2__emitted', 'steel'],
                compare_inflows=False,
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=f'output/test_{today}/EUROFER Industry')

# EVOLVE INDUSTRY - EU BECCS
dat.outdir = f'output/test_{today}/EU Industry'

EU_industry_dict = {'steel-EU28-PBC': dict(factory_list_file='data/steel/steel_industry_EU28-Plausible.xlsx',
                    factory_list_sheet='Factory List', 
                    name='EU Plausible BECCS',
                    steps=[1990, 2010, 2015, 2030, 2050],
                    step_sheets=['1990', '2010', '2015', '2030', '2050'], 
                    write_to_xls=write_to_xls, 
                    graph_outflows=['CO2__emitted', 'crude steel'],
                    graph_inflows=False),
                    }

com.test_industry_evolve(
                EU_industry_dict,
                qty=qty, 
                compare_evolved_industres=False,
                compare_industry_name='EU-28 Steel',
                compare_steps=[1990, 2010, 2015, 2030, 2050],
                compare_step_sheets=['1990', '2010', '2015', '2030', '2050'],
                compare_outflows=False,
                compare_inflows=False,
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=f'output/test_{today}/EU Industry',
                )

# EVOLVE INDUSTRY - CHINA

