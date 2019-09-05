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
# COMPARE BECCS



BF_factory_dict = {
                'IBC-0C': dict(chain_list_file="data/steel/factories/IBF_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF wo CCS",
                                        scenario='BBF-0B'),
                'IBC-LC': dict(chain_list_file="data/steel/factories/IBF-factory-BFG CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF w BFG-only CCS",
                                        scenario='BBF-0B'),
                'IBC-HC': dict(chain_list_file="data/steel/factories/IBF_factory-CCS.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="BF-BOF w CCS",
                                        scenario='BBF-0B'),
}

dat.outdir = f'{outdir}/BBF'
com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-0B', 'BBF-LB', 'BBF-HB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BBF')


dat.outdir = f'{outdir}/TGR/'
com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['TGR-0B', 'TGR-LB', 'TGR-HB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/TGR')

dat.outdir = f'{outdir}/HIS/'
com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['HIS-0B', 'HIS-LB', 'HIS-HB',], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/HIS')

###############################################################################
# COMPARE TECHNOLOGIES

dat.outdir = f'{outdir}/BF-multitech/None'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-0B', 'TGR-0B', 'HIS-0B'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/None')


dat.outdir = f'{outdir}/BF-multitech/Low Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-LB', 'TGR-LB', 'HIS-HB'], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/Injectant')


dat.outdir = f'{outdir}/BF-multitech/High Biomass'

com.test_factory_scenarios(factory_dict=BF_factory_dict,
                        scenario_factories=['IBC-0C', 'IBC-LC', 'IBC-HC'], 
                        scenario_product=False,
                        scenario_unit=False,
                        scenario_io=False,
                        qty=qty, 
                        scenario_list=['BBF-HB', 'TGR-HB', 'HIS-HB',], 
                        write_to_console=write_to_console, 
                        write_to_xls=write_to_xls,
                        view_diagrams=view_diagrams,
                        save_diagrams=save_diagrams,
                        outdir=f'{outdir}/BECCS-multiregion/Plausible')




###############################################################################
# DRI

DRI_factory_dict = {
                'DRI-0C': dict(chain_list_file="data/steel/factories/DRI_factory.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF wo CCS",
                                        scenario='MID-0B'),
                'DRI-LC': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs-bfonly.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF w DRI-only CCS",
                                        scenario='MID-0B'),
                'DRI-HC': dict(chain_list_file="data/steel/factories/steel_simplified_factory-ccs.xlsx",
                                        chain_list_sheet='chains', 
                                        connections_sheet='connections', 
                                        name="DRI-EAF w CCS",
                                        scenario='MID-0B'),
}

###############################################################################
# Sensitivity Analysis
dat.outdir = f'{outdir}/Electricity'

electricity_factory_dict= {
            'Simplified Steel-GtG': dict(chain_list_file="data/steel/factories/steel_simplified_factory-noupstream.xlsx",
                                chain_list_sheet='chains', 
                                connections_sheet='connections', 
                                name="BF-BOF Steel Mill",
                                scenario='US-0B',
                                outdir=f'{outdir}/Electricity'),
}

com.test_factory_sensitivity(factory_dict=electricity_factory_dict,
                            scenario_factories=['Simplified Steel-GtG'], 
                            scenario='BBF-0B',
                            chain_name='steel', 
                            unit_name='simple_electricity', 
                            variable='fueltype', 
                            variable_options=['natural gas - IPCC', 'electricity - EU 2016', 'electricity - decarbonized'],
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=f'{outdir}/Electricity')