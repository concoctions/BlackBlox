import random
import pandas as pan
from pprint import pprint
from datetime import datetime

import io_functions as iof
import dataconfig as dat
import unitprocess as uni
import processchain as cha
import factory as fac
import industry as ind


# USER DATA CONFIG
dat.outdir = "output/demo"

dat.user_data = {"name": "S.E. Tanzer",
             "affiliation": "TU Delft",
             "project": f"BlackBlox Demo - {datetime.now().strftime('%d %B %Y')}",
}

dat.default_units = {'mass': 'tonnes', 
                 'energy':'GJ',
}

print("\n\nWELCOME\n\n")

input("\n\n\nPress enter to start demo: ")

print(f"\n\nblackblox.py v0.0.2 Demonstration")
print(f"{datetime.now().strftime('%A, %d %B %Y at %H:%M')}")

print(f"\nUsing unit process data from {dat.unit_process_library_file}")
print(f"and outputting any files to {dat.outdir}")

print('\nNOTE: Throughout this demo, directly pressing ENTER moves you forward one step,\n' 
        'while entering a character skips to the next part of the demonstration')

input('\n\n\nPress enter to continue: ')   
##############################################################################
## UNIT PROCESS TEST
##############################################################################
print('\n\n\nUNIT PROCESS TEST - outputs to console.')

stop = input("\nPress enter to balance the KILN unit process: ")

while stop == '':
    if stop != '':
        break
    unit_list =uni.df_unit_library.index.tolist()
    kiln = uni.UnitProcess('demo_kiln')
    qty = round(random.uniform(10, 1000),2)
    product = kiln.default_product

    scenarios = kiln.var_df.index.tolist()
    s = random.choice(scenarios)

    print("\n",str.upper(kiln.name))
    print("\ninflows:", ', '.join(kiln.inflows))
    print("outflows:", ', '.join(kiln.outflows))
    print(f"\nbalacing {kiln.name} on {qty}  of {product} ({kiln.default_io}) using {s} values")

    u_in, u_out = kiln.balance(qty, scenario=s)
    print("\ncalculated inflow quantities:")
    for k, v in u_in.items():
        print(f'  {k}: {v}')
    print("\ncalculated outflow quantities:")
    for k, v in u_out.items():
        print(f'  {k}: {v}')

    stop = input(f"\n\n\nPress enter to balance {kiln.name} on a random inflow: ")
    if stop != '':
        break

    print(f"\nselecting random inflow...")
    product = random.choice(tuple(kiln.inflows))
    if product == 'fuel':
            qty = u_in[kiln.var_df.at[s, 'fueltype']]
    else:
        qty = u_in[product]
    print(f"\nnow balacing {kiln.name} on {qty} {dat.default_units['mass']} of {product} ({'inflow'}) using {s} values")

    u1_in, u1_out = kiln.balance(qty, product, 'i', s) 
        
    rounded_u_in = {k:round(v, 6) for k, v in u_in.items()}
    rounded_u_out = {k:round(v, 6) for k, v in u_out.items()}
    rounded_u1_in = {k:round(v, 6) for k, v in u1_in.items()}
    rounded_u1_out = {k:round(v, 6) for k, v in u1_out.items()}
    if rounded_u1_in == rounded_u_in and rounded_u1_out == rounded_u_out:
        print("\nSame input/output as above, rounded to 6 decimal places")
    else:
        print("\n [!] not equivelent to above [!]\n")
        print("recalculated inflow quantities:")
        for k, v in u1_in.items():
            print(f'  {k}: {v}')
        print("\ncalculated outflow quantities:")
        for k, v in u1_out.items():
            print(f'  {k}: {v}')

    stop = input(f"\n\n\nPress enter to test 1-to-1 recycle on {product} (inflow): ")
    if stop != '':
        break
    
    qty_recycled = round(qty*random.uniform(0.01, 0.99),2)
    max_replace_fraction = round(random.uniform(0.01, 1.0),2)
    print(f"\nRecycling {qty_recycled} of RECYCLED FLOW 1-to1 for not more than {max_replace_fraction*100}% of {product}") 

    r1_in, r1_out, leftover = kiln.recycle_1to1(original_inflows_dict=u_in,
                                                       original_outflows_dict=u_out,
                                                       recycled_qty=qty_recycled,
                                                       recycle_io='i',
                                                       recycled_flow='RECYCLED FLOW',
                                                       replaced_flow=product,
                                                       max_replace_fraction=max_replace_fraction,
                                                       scenario=s)
    
    print("\nrecalculated inflow quantities:")
    for k, v in r1_in.items():
        print(f'  {k}: {v}')
    rounded_r1_out = {k:round(v, 6) for k, v in r1_out.items()}
    if rounded_r1_out == rounded_u_out:
        print("\nSame outflow as above, rounded to 6 decimal places")
    else:
        print("\n [!] outflows not equivelent to above [!]\n")
        print("recalculated outflow quantities:")
        for k, v in r1_out.items():
            print(f'  {k}: {v}')
    print(f"\nRECYCLE FLOW leftover: {leftover}")
            
    stop = input(f"\n\n\nPress enter to balance {kiln.name} on a random outflow: ")
    if stop != '':
        break

    print(f"\nselecting random outflow...")
    product = random.choice(tuple(kiln.outflows))
    while product == 'slag':
        print('cannot balance on slag, because slag is calculated as a remainder of an inflow and outflow. Selecting alternate outflow.')
        product = random.choice(tuple(kiln.outflows))
    if product == 'fuel':
            qty = u_out[kiln.var_df.at[s, 'fueltype']]

    qty = u_out[product]
    print(f"\nnow balacing {kiln.name} on {qty} of {product} ({'outflow'}) using {s} values")

    u1_in, u1_out = kiln.balance(qty, product, 'o', s) 
        
    rounded_u1_in = {k:round(v, 6) for k, v in u1_in.items()}
    rounded_u1_out = {k:round(v, 6) for k, v in u1_out.items()}
    if rounded_u1_in == rounded_u_in and rounded_u1_out == rounded_u_out:
        print("\nSame input/output as above, rounded to 6 decimal places")
    else:
        print("\n [!] not equivelent to above [!]\n")
        print("\ncalculated inflow quantities:")
        for k, v in r1_in.items():
            print(f'  {k}: {v}')
        print("\ncalculated outflow quantities:")
        for k, v in r1_out.items():
            print(f'  {k}: {v}')
        if product in dat.default_emissions or product == 'waste heat':
            print(f"\n(Since this was {product}, which has multiple sources, this was expected.)")

        stop = input(f"\n\n\nPress enter to test 1-to-1 recycle on {product} (outflow): ")
        if stop != '':
            break

        qty_recycled = round(qty*random.uniform(1.1, 10),2)
        max_replace_fraction = round(random.uniform(0.01, 1),2)
        print(f"\nRecycling {qty_recycled} of RECYCLED FLOW 1-to1 for not more than {max_replace_fraction}% of {product}") 

        r1_in, r1_out, leftover = kiln.recycle_1to1(original_inflows_dict=u_in,
                                                           original_outflows_dict=u_out,
                                                           recycled_qty=qty_recycled,
                                                           recycle_io='o',
                                                           recycled_flow='RECYCLED FLOW',
                                                           replaced_flow=product,
                                                           max_replace_fraction=max_replace_fraction,
                                                           scenario=s)

        rounded_r1_in = {k:round(v, 6) for k, v in r1_in.items()}
        if rounded_r1_in == rounded_u_in:
            print("\nSame inflows as above, rounded to 6 decimal places")
        else:
            print("\n [!] inflows not equivelent to above [!]\n")
            print("recalculated inflows quantities:")
            for k, v in r1_in.items():
                print(f'{k}: {v}')    
        print("\nrecalculated outflow quantities:")
        for k, v in r1_out.items():
            print(f'  {k}: {v}')
        print(f"\nRECYCLE FLOW leftover: {leftover}")

    fuel_type = kiln.var_df.at[s, 'fueltype']
    fuel_qty =  u_in[kiln.var_df.at[s, 'fueltype']]
    recycled_energy_qty = round(fuel_qty * random.uniform(30,100),2)
    max_replace_fraction = round(random.uniform(0.01, 1.0),2)

    stop = input(f"\n\n\nPress enter to recycle energy to replace {fuel_type} (inflow) in  {kiln.name}")


    print(f"\nRecycling {recycled_energy_qty} {dat.default_units['energy']} of RECYCLED ENERGY into {kiln.name} replacing no more than {max_replace_fraction*100}% of {fuel_type})") 

    r1_in, r1_out, leftover = kiln.recycle_energy_replacing_fuel(original_inflows_dict=u_in,
                                                                        original_outflows_dict=u_out,
                                                                        recycled_qty=recycled_energy_qty,
                                                                        recycle_io="inflow",
                                                                        recycled_flow="RECYCLED ENERGY",
                                                                        replaced_flow=fuel_type,
                                                                        max_replace_fraction=max_replace_fraction,
                                                                        combustion_eff = dat.combustion_efficiency_var,
                                                                        scenario=s,
                                                                        emissions_list = dat.default_emissions)

    print("\nrecalculated inflow quantities:")
    for k, v in r1_in.items():
        print(f'  {k}: {v}')
    print("\nrecalculated outflow quantities:")
    for k, v in r1_out.items():
        print(f'  {k}: {v}')
    print(f"\nRECYCLE FLOW leftover: {leftover}")

    stop = 'stop'
    
input('\n\n\nPress enter to continue: ')  

##############################################################################
## PROCESS CHAIN TEST
##############################################################################
factory_file = "data/demo/factories/cementFactory_withCCS.xlsx"
df_cols = ['mixer', 'kiln', 'blender', 'chain totals']

print("\n\n\nPROCESS CHAIN TEST - outputs to console. ")
stop = input('\nPress enter to create a CEMENT production chain object or type any character to skip: ')
while stop == '':
    if stop != '':
        break

    cement_chain = cha.ProductChain(chain_data=factory_file, 
                                    name= "Cement Production", 
                                    xls_sheet='Cement Chain')

    cement_chain.build()
    print('\nCEMENT Chain Data:')
    pprint(cement_chain.process_chain_df)

    stop = input("\n\n\nPress enter to generate CEMENT chain proces diagram: ")
    if stop != '':
        break
    cement_chain.diagram(view=True, save=False)
    print("\nDiagram sent to system viewer.")

    stop = input("\n\n\nPress enter to balance the cement chain on 1.0 tonnes of cement out: ")
    if stop != '':
        break    

    chain_inflows, chain_outflows, int_flows, int_rows = cement_chain.balance(1.0)
    chain_inflows = pan.DataFrame(chain_inflows)
    chain_inflows = chain_inflows[df_cols]
    chain_inflows = iof.mass_energy_df(chain_inflows)
    chain_outflows = pan.DataFrame(chain_outflows)
    chain_outflows = chain_outflows[df_cols]
    chain_outflows = iof.mass_energy_df(chain_outflows)

    print("\ncement chain inflows:\n", chain_inflows)
    print("\ncement chain outflows:\n", chain_outflows)

    print("\ncement chain intermediate flows:")
    for row in int_rows:
        print(row)

    stop = input("\n\n\nPress enter to balance the cement chain on 1.070880 of CaCO3 in: ")
    if stop != '':
        break  
    inflows, outflows, int_flows, int_rows = cement_chain.balance(1.070880, product="CaCO3", scenario="default")
    inflows = pan.DataFrame(inflows)
    inflows = inflows[df_cols]
    inflows = iof.mass_energy_df(inflows)

    outflows = pan.DataFrame(outflows)
    outflows = outflows[df_cols]
    outflows = iof.mass_energy_df(outflows)

    print("\ncement chain inflows:\n", inflows)
    print("\ncement chain outflows:\n", outflows)

    stop = input("\n\n\nPress enter to balance the cement chain on 0.8 of clinker out of the kiln: ")
    if stop != '':
        break  

    inflows, outflows, int_flows, int_rows = cement_chain.balance(0.8, product="clinker", i_o='outflow', unit_process='demo_kiln', scenario="default")
    inflows = pan.DataFrame(inflows)
    inflows = inflows[df_cols]
    outflows = pan.DataFrame(outflows)
    outflows = outflows[df_cols]

    print("\n")
    print("\ncement chain inflows:\n", inflows)
    print("\ncement chain outflows:\n", outflows)


    stop = 'stop'

input('\n\n\nPress enter to continue: ')  

##############################################################################
## FACTORY TEST
##############################################################################
print('\n\n\nINTERLINKED FACTORY TEST - outputs to console and file.')
stop = input('\nPress enter to proceed or type any character to skip: ')
while stop == '':
    if stop != '':
        break

    cement_factory = fac.Factory(chain_list_file=factory_file,
                                 chain_list_sheet='Chain List', 
                                 connections_sheet='Connections', 
                                 name="Cement with CCS")

    print(f"\n{cement_factory.name} factory")
    print(f"\nchains in this factory:")
    # print(cement_factory.chains_df)
    # print("\n connections in this factory:")
    # print(cement_factory.connections_df[['o product', 'o chain', 'o unit', ' d chain', 'd unit', 'r replacing']])
    
    # stop = input("\n\n\nPress enter to see all connection data for waste heat recycling: ")
    # if stop != '':
    #     break
    # print("\n",cement_factory.connections_df.iloc[3, :])
    
    stop = input("\n\n\nPress enter to generate a diagram of the cement factory: ")
    if stop != '':
        break
    cement_factory.diagram(view=True, save=False)
    print("\nDiagram sent to system viewer.")

    stop = input("\n\n\nPress enter to balance the factory on 100.0 tonnes of cement (outputs to file): ")
    if stop != '':
        break
    inflows, outflows = cement_factory.balance(product_qty = 100, 
                                                scenario=dat.default_scenario, 
                                                write_to_xls=True, 
                                                outdir=dat.outdir, 
                                                mass_energy=True, 
                                                energy_flows=dat.energy_flows)

    totals = {'factory inflows': inflows, 'factory outflows': outflows}
    totals = pan.DataFrame(totals)
    totals = iof.mass_energy_df(totals)
    print(f"\n{cement_factory.name} total inflows and outflows")
    print(totals)
    print("\n Full results available in demo_output directory.")


    stop = input("\n\n\nPress enter to balance the factory on 10.68249258 tonnes of fuel inflow to kiln (outputs to file): ")
    inflows, outflows = cement_factory.balance(product_qty = 10.68249258, 
                                                product = 'fuel',
                                                product_io = 'inflow',
                                                product_unit = 'demo_kiln',
                                                scenario=dat.default_scenario, 
                                                write_to_xls=True, 
                                                outdir=dat.outdir, 
                                                mass_energy=True, 
                                                energy_flows=dat.energy_flows)

    totals = {'factory inflows': inflows, 'factory outflows': outflows}
    totals = pan.DataFrame(totals)
    totals = iof.mass_energy_df(totals)
    
    print(f"\n{cement_factory.name} total inflows and outflows")
    print(totals, "\n")
    print("\n Full results available in demo_output directory")

    stop = 'stop'

input('\n\n\nPress enter to continue: ')  

###############################################################################
## INDUSTRY TEST
###############################################################################
industry_file = "data/demo/cementIndustry.xlsx"

print('\n\n\nINDUSTRY TEST - outputs to file.')
stop = input('\nPress enter or type a character to skip: ')

i_kwargs = dict(factory_list_file=industry_file,
                factory_list_sheet='Factory List', 
                name='Cement Industry')

industry = ind.Industry(**i_kwargs)

industry.build()

print("\nThe Toy Cement Industry consists of the following factories:")
for factory, details in industry.factory_dict.items():
    print("  ",details['name'])


while stop == '':
    stop = input("\n\n\nPress enter to balance the toy cement industry, producing 3500 tonnes of cement in the year 2000: ")
    if stop != '':
        break
    print("\nworking....")

    ioDicts= industry.balance(production_data_sheet='2000', write_to_xls=True, 
                    file_id='2010', diagrams=True)
            
    print("\nDone. Files available in demo_output directory.")

    stop = input("\n\n\nPress enter to compare scenarios of production in the cement industry: ")
    if stop != '':
        break    

    print("\nusing scenario variable values for:")
    s_list = ['EU-1990', 'EU-2000', 'EU-2010', 'EU-BECCS']
    for s in s_list:
        print("  ",s)

    print("\nworking...")
    

    s_kwargs = dict(scenario_list=s_list, 
                    products_sheet='2010', 
                    write_to_xls=True, 
                    file_id='2010', 
                    diagrams=False)

    industry.run_scenarios(**s_kwargs)

    print("\nDone. Files available in demo_output directory.")

    stop = input("\n\n\nPress enter to model the cement industry from 1990 to 2010 and generate outflow graphs for cement and CO2: ")
    if stop != '':
        break  
    print("\nworking....\n")

    e_kwargs = dict(start_sheet='1990', 
                    end_sheet='2010',
                    start_step=1990,
                    end_step=2010,
                    write_to_xls=True, 
                    diagrams=True,
                    graph_outflows = ['CO2', 'cement'])
    industry.evolve(**e_kwargs)

    print("Done. Files available in demo_output directory.")

    stop = input("\n\n\nPress enter to model the cement industry from 1990 to 2000 to 2010 and generate outflow graphs for cement and CO2: ")
    if stop != '':
        break 
    print("\nworking....")

    m_kwargs = dict(steps=[1990,2000,2010], 
                    production_data_files=None, 
                    step_sheets=['1990', '2000', '2010'], 
                    file_id='',
                    outdir=dat.outdir, 
                    write_to_xls=True, 
                    graph_outflows = ['CO2', 'cement'])
    industry.evolve_multistep(**m_kwargs)

    print("\nDone. Files available in demo_output directory.")
    stop = 'stop'

input("\n\n\nPress enter to end demo. \n")

print('\n\n\nGOOD BYE.\n\n')