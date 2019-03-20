"""TESTING FILE
"""

import pandas as pan
import io_functions as iof
import dataconfig as dat
import unitprocess as uni
import processchain as cha
import factory as fac

test_units = False
test_chains = False
test_factories = True

diagrams = False
write_to_xls = True

qty = 1
scenario = 'IEAGHG 2013'

unit_list = [
            'IEAGHGsteel_coke_oven',
            'IEAGHGsteel_sinter_plant',
            'IEAGHGsteel_blast_furnace', 
            'IEAGHGsteel_BOF',
            'IEAGHGsteel_ladle',
            'IEAGHGsteel_forming',
            'aux_lime kiln',
            'aux_air separation',
            'electricity_1step',
            'heat_collector',
             ]

chain_dict = {
              'steel': dict(name='steel',
                            chain_data="data/steel/steel_factories.xlsx",
                            xls_sheet='steel chain'),
}

factory_dict = {
                'reference steel': dict(chain_list_file="data/steel/steel_factories.xlsx",
                                        chain_list_sheet='ref chains', 
                                        connections_sheet='ref connections', 
                                        name="Reference Steel Plant")}

# UNIT TEST
if test_units is True:
    for unit_id in unit_list:
        unit = uni.UnitProcess(unit_id)

        print(str.upper(unit.name))
        print("\ninflows:", ', '.join(unit.inflows))
        print("outflows:", ', '.join(unit.outflows))
        u_in, u_out = unit.balance(qty, scenario=scenario)

        flows = iof.make_df(dict(inflows=u_in, outflows=u_out))
        flows = iof.mass_energy_df(flows)
        print(flows)


# CHAIN TEST
if test_chains is True:
    for c in chain_dict:
        chain = cha.ProductChain(**chain_dict[c])
        chain.build()

        if diagrams is True:
            chain.diagram(view=True, save=False)
        
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

        if diagrams is True:
            factory.diagram(view=True, save=False)

        inflows, outflows = factory.balance(product_qty = qty, 
                                            scenario=scenario, 
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
            print("\n Full results available in demo_output directory.")