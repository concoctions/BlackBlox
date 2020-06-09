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



# COMPARE REGIONAL BASE TECHNOLOGY

dat.outdir = f'{outdir}/RegionCompare'

base_factory_dict= {
            'Simplified Steel-GtG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-noupstream.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='EU-0B'),
}


com.test_factory_scenarios(base_factory_dict,
                        ['Simplified Steel-GtG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-0B', 'CH-0B', 'JP-0B', 'RU-0B', 'US-0B', 'IN-0B'], 
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
                                scenario='US-0B',
                                outdir=f'{outdir}/ScrapRatio'),
}

com.test_factory_sensitivity(factory_dict=scrap_factory_dict,
                            scenario_factories=['Simplified Steel-GtG'], 
                            scenario='US-0B',
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
# COMPARE BECCS - REGIONAL TECH 



BECCS_factory_dict = {
                    'Steel': dict(chain_list_file="data/steel/factories/steel_simplified_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF",
                                        scenario='EU-0B'),
                'Steel_CCS-max': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-max",
                                        scenario='EU-0B'),
                'Steel_CCS-BF': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs-bfonly.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-BFG",
                                        scenario='EU-0B'),
                'Steel_CCS-BF-COG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs-bfcoke.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF CCS-BFGCOG",
                                        scenario='EU-0B'),
}

dat.outdir = f'{outdir}/BECCS-EU-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-0B', 'EU-IB', 'EU-CB', 'EU-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-EU-Factory')


dat.outdir = f'{outdir}/BECCS-CN-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['CH-0B', 'CH-IB', 'CH-CB', 'CH-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-CN-Factory')


dat.outdir = f'{outdir}/BECCS-IN-Factory'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['IN-0B', 'IN-IB', 'IN-CB', 'IN-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-IN-Factory')


###############################################################################
# COMPARE BECCS - Multiregion


dat.outdir = f'{outdir}/BECCS-multiregion/None'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['EU-0B', 'CH-0B', 'IN-0B'], 
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
                        scenario_list=['EU-IB', 'CH-IB', 'IN-IB'], 
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
                        scenario_list=['EU-CB', 'CH-CB', 'IN-CB',], 
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
                        scenario_list=['EU-TB', 'CH-TB', 'IN-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/Theoretical')



###############################################################################
# 2050 Technologies

dat.outdir = f'{outdir}/2050 Tech/BF-SOA/'

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
                        outdir=f'{outdir}/2050 Tech/BF-SOA/')

dat.outdir = f'{outdir}/2050 Tech/BF-TGR/'

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
                        outdir=f'{outdir}/2050 Tech/BF-TGR')

dat.outdir = f'{outdir}/2050 Tech/BF-TMin/'

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
                        outdir=f'{outdir}/2050 Tech/BF-TMin')


dat.outdir = f'{outdir}/2050 Tech/HIsarna/'

com.test_factory_scenarios(factory_dict=BECCS_factory_dict,
                        scenario_factories=['Steel', 'Steel_CCS-max', 'Steel_CCS-BF', 'Steel_CCS-BF-COG'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['HIS-0B', 'HIS-IB', 'HIS-CB', 'HIS-TB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/2050 Tech/HIsarna')

###############################################################################
# Charcoal Impacts

dat.outdir = f'{outdir}/ScrapRatio'

scrap_factory_dict= {
            'Simplified Steel-GtG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-noupstream.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='US-0B',
                                outdir=f'{outdir}/ScrapRatio'),
}

com.test_factory_sensitivity(factory_dict=scrap_factory_dict,
                            scenario_factories=['Simplified Steel-GtG'], 
                            scenario='US-0B',
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

# fuel options

# Regional Coals

# Biomass options 


###############################################################################
# CO2 storage options

# Different CO2 Capture options

# EOR

# Greenhouses