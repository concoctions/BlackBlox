"""TESTING FILE
"""

import dataconfig as dat
from datetime import datetime

dat.outdir = "output/test"

dat.user_data = {"name": "S.E. Tanzer",
             "affiliation": "TU Delft",
             "project": f"Steel tests - {datetime.now().strftime('%d %B %Y')}",
}

dat.default_units = {'mass': 'tonnes', 
                 'energy':'GJ',
}

import pandas as pan
import io_functions as iof
import unitprocess as uni
import processchain as cha
import factory as fac

test_units = False
test_chains = False
test_factories = True

view_diagrams = False
save_diagrams = True
write_to_xls = True

qty = 1.0

scenario = 'birat-tgr-63vpsa-50bio'

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

chain_dict = {
              'steel': dict(name='steel',
                            chain_data="data/steel/steel_factories.xlsx",
                            xls_sheet='steel chain'),
}

factory_dict = {
                'IEAGHG steel': dict(chain_list_file="data/steel/IEAGHG_factories.xlsx",
                                        chain_list_sheet='IEAGHG chains', 
                                        connections_sheet='IEAGHG connections', 
                                        name="IEAGHG Steel Plant",
                                        scenario='IEAGHG 2013'),
                'Birat steel base': dict(chain_list_file="data/steel/birat_factories.xlsx",
                                        chain_list_sheet='base chains', 
                                        connections_sheet='base connections', 
                                        name="BF Steel Plant",
                                        scenario='birat-base'),
                'Birat CCS': dict(chain_list_file="data/steel/birat_factories.xlsx",
                                        chain_list_sheet='TGR-CCS chains', 
                                        connections_sheet='TGR-CCS connect', 
                                        name="BF-TGR-CCS Steel Plant",
                                        scenario='birat-tgr-63vpsa'),
                'Birat BECCS': dict(chain_list_file="data/steel/birat_factories.xlsx",
                                        chain_list_sheet='TGR-CCS chains', 
                                        connections_sheet='TGR-CCS connect', 
                                        name="BF-TGR-BECCS Steel Plant",
                                        scenario='birat-tgr-63vpsa-50bio'),
                'Birat BECCS+upstream': dict(chain_list_file="data/steel/birat_factories.xlsx",
                                        chain_list_sheet='BECCS chains', 
                                        connections_sheet='BECCS connect', 
                                        name="BF-TGR-CCS Steel with Upstream",
                                        scenario='birat-tgr-63vpsa-50bio'),
}

# UNIT TEST
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

        flows = iof.make_df(dict(inflows=u_in, outflows=u_out))
        flows = iof.mass_energy_df(flows)
        print(flows)


# CHAIN TEST
if test_chains is True:
    for c in chain_dict:
        chain = cha.ProductChain(**chain_dict[c])
        chain.build()

        if view_diagrams is True or save_diagrams is True:
            chain.diagram(view=view_diagrams, save=save_diagrams)
        
        print(chain.process_dict)

        chain_inflows, chain_outflows, int_flows, int_rows = chain.balance(qty, scenario=scenario)
        chain_inflows = iof.make_df(chain_inflows)
        chain_inflows = iof.mass_energy_df(chain_inflows)
        chain_outflows = iof.make_df(chain_outflows)
        chain_outflows = iof.mass_energy_df(chain_outflows)

        print("\ninflows:\n", chain_inflows)
        print("\noutflows:\n", chain_outflows)

        print("\nintermediate flows:")
        for row in int_rows:
            print(row)

# FACTORIES TEST
if test_factories is True:
    for f in factory_dict:

        factory = fac.Factory(**factory_dict[f])
        factory.build()
        print(f"\n{factory.name} factory")

        if view_diagrams is True or save_diagrams is True:
            factory.diagram(view=view_diagrams, save=save_diagrams)

        inflows, outflows = factory.balance(product_qty = qty, 
                                            scenario=factory_dict[f]['scenario'], 
                                            write_to_xls=write_to_xls, 
                                            outdir=dat.outdir, 
                                            mass_energy=True, 
                                            energy_flows=dat.energy_flows)

        totals = {'factory inflows': inflows, 'factory outflows': outflows}
        totals = pan.DataFrame(totals)
        totals = iof.mass_energy_df(totals)
        print(f"\n{factory.name} total inflows and outflows")
        print(totals)

        if write_to_xls is True:
            print(f"\n Full results available in {dat.outdir} directory.")