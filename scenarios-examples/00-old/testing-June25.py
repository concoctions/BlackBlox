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
# REPLICATE BIRAT

dat.outdir = f'{outdir}/Birat'

factory_dict = {
                'Simplified Steel': dict(chain_list_file="data/steel/factories/steel_simplified_factory-birat.xlsx",
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
                outdir=f'{outdir}/Birat')


###############################################################################
# COMPARE LEVEL OF DETAIL

dat.outdir = f'{outdir}/LevelOfDetail'

LoD_factory_dict = {
                'Detailed Steel-Crude': dict(chain_list_file="data/steel/factories/IEAGHG_factory-crudesteel.xlsx",
                                            chain_list_sheet='IEAGHG chains', 
                                            connections_sheet='IEAGHG connections', 
                                                    name="BF Steel (IEAGHG)",
                                                    scenario='ieaghg-reference'),
                'Birat Steel': dict(chain_list_file="data/steel/factories/birat_factories.xlsx",
                                        chain_list_sheet='base chains', 
                                        connections_sheet='base connections', 
                                        name="BF Steel (IEAGHG-Birat)",
                                        scenario='ieaghg-reference'),
                'Simplified Steel-IEAGHG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ieaghg.xlsx",
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
                outdir=f'{outdir}/LevelOfDetail')


###############################################################################
# COMPARE REGIONAL BASE TECHNOLOGY

dat.outdir = f'{outdir}/RegionCompare'

base_factory_dict= {
            'Simplified Steel-GtG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-noupstream.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='EU-0B-2015'),
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
                        outdir=f'{outdir}/RegionCompare')



###############################################################################
# SCRAP RATIO SENSITIVITY

dat.outdir = f'{outdir}/ScrapRatio'

scrap_factory_dict= {
            'Simplified Steel-GtG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-noupstream.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='US-0B-2015',
                                outdir=f'{outdir}/ScrapRatio'),
}

com.test_factory_sensitivity(factory_dict=scrap_factory_dict,
                            scenario_factories=['Simplified Steel-GtG'], 
                            scenario='US-0B-2015',
                            chain_name='steel', 
                            unit_name='simple_BOF', 
                            variable='scrap demand', 
                            variable_options=[0.0, 0.1, 0.2, 0.3, 0.4],
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}/ScrapRatio')

                          
###############################################################################
# COMPARE BECCS - BASE TECH - EU

dat.outdir = f'{outdir}/BECCS-EU-Factory'

BECCS_factory_dict = {
                    'Steel': dict(chain_list_file="data/steel/factories/steel_simplified_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF",
                                        scenario='EU-0B-2015'),
                'Steel_CCS-max': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-max",
                                        scenario='EU-0B-2015'),
                'Steel_CCS-BF': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs-bfonly.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-BFG",
                                        scenario='EU-0B-2015'),
                'Steel_CCS-BF-COG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs-bfcoke.xlsx",
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
                        scenario_list=['EU-0B-2015', 'EU-IB-2015', 'EU-CB-2015', 'EU-TB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-EU-Factory/2015')




###############################################################################
# COMPARE BECCS - BASE TECH - CHINA

dat.outdir = f'{outdir}/BECCS-CN-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['CH-0B-2015', 'CH-IB-2015', 'CH-CB-2015', 'CH-TB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-CN-Factory/2015')


###############################################################################
# COMPARE BECCS - BASE TECH - India, Japan, Russia, USA

dat.outdir = f'{outdir}/BECCS-IN-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['IN-0B-2015', 'IN-IB-2015', 'IN-CB-2015', 'IN-TB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-IN-Factory/2015')

dat.outdir = f'{outdir}/BECCS-JP-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['JP-0B-2015', 'JP-IB-2015', 'JP-CB-2015', 'JP-TB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-JP-Factory/2015')


dat.outdir = f'{outdir}/BECCS-RU-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['RU-0B-2015', 'RU-IB-2015', 'RU-CB-2015', 'RU-TB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-RU-Factory/2015')

dat.outdir = f'{outdir}/BECCS-US-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['US-0B-2015', 'US-IB-2015', 'US-CB-2015', 'US-TB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-US-Factory/2015')


###############################################################################
# COMPARE BECCS - Multiregion


dat.outdir = f'{outdir}/BECCS-multiregion/None'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-0B-2015', 'CH-0B-2015', 'JP-0B-2015', 'IN-0B-2015', 'RU-0B-2015', 'US-0B-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/None')


dat.outdir = f'{outdir}/BECCS-multiregion/Injectant'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-IB-2015', 'CH-IB-2015', 'JP-IB-2015', 'IN-IB-2015', 'RU-IB-2015', 'US-IB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/Injectant')


dat.outdir = f'{outdir}/BECCS-multiregion/Plausible'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-CB-2015', 'CH-CB-2015', 'JP-CB-2015', 'IN-CB-2015', 'RU-CB-2015', 'US-CB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/Plausible')


dat.outdir = f'{outdir}/BECCS-multiregion/Theoretical'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty,
                        scenario_list=['EU-TB-2015', 'CH-TB-2015', 'JP-TB-2015', 'IN-TB-2015', 'RU-TB-2015', 'US-TB-2015'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/Theoretical')



###############################################################################
# INDUSTRY - scale up units

dat.default_units = {'mass': 'Mt', 
                     'energy':'PJ',
}

importlib.reload(iof)


###############################################################################
# BECCS TO INDUSTRY

dat.outdir = f'{outdir}/Global Industry 2015'

BECCS_industry_dict = { 'Base': dict(factory_list_file='data/steel/industries/steel_industry_6countries.xlsx',
                                factory_list_sheet='Factory List', 
                                production_data_sheet='Base',
                                name='Base',
                                write_to_xls=write_to_xls),
                        'Bioenergy': dict(factory_list_file='data/steel/industries/steel_industry_6countries.xlsx',
                                factory_list_sheet='Factory List', 
                                production_data_sheet='Bioenergy',
                                name='Bioenergy',
                                write_to_xls=write_to_xls),
                        'CCS': dict(factory_list_file='data/steel/industries/steel_industry_6countries.xlsx',
                                factory_list_sheet='Factory List', 
                                production_data_sheet='CCS',
                                name='CCS',
                                write_to_xls=write_to_xls),
                        'BECCS': dict(factory_list_file='data/steel/industries/steel_industry_6countries.xlsx',
                                factory_list_sheet='Factory List', 
                                production_data_sheet='BECCS',
                                name='BECCS',
                                write_to_xls=write_to_xls),
                        }

com.test_industries(BECCS_industry_dict,
                industry_name='global',
                scenario_id='2015', 
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=f'{outdir}/Global Industry 2015')

###############################################################################
# 2050 Technologies
dat.outdir = f'{outdir}/2050 Tech'


com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['SOA-0B', 'SOA-IB', 'SOA-CB', 'SOA-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/SOA/')


com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['TGR-0B', 'TGR-IB', 'TGR-CB', 'TGR-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/TGR')

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['TMIN-0B', 'TMIN-IB', 'TMIN-CB', 'TMIN-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/TMIN')


###############################################################################
# fuel options

# Regional Coals

# Biomass options 


###############################################################################
# CO2 storage options

# Different CO2 Capture options

# EOR

# Greenhouses