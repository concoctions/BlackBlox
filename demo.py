import random
import pandas as pan
from pprint import pprint
from datetime import datetime

import dataconfig as dat
import unitprocess as uni
import processchain as cha
import factory as fac


# USER DATA CONFIG
my_filepaths = {'unit_process_library_file': "/Users/Tanzer/GitHub/BlackBlox/demoData/toy cement/toycement_unitlibrary.xls",
             'unit_process_library_sheet': None,
             'outdir': "demo_output",
}

my_user_data = {"name": "S.E. Tanzer",
             "affiliation": "TU Delft",
             "project": f"BlackBlox Demo - {datetime.now().strftime('%d %B %Y')}",
}

my_lookup_var_dict = { 
    'fuel': dict(filepath='/Users/Tanzer/GitHub/BlackBlox/demoData/fuels.xlsx',
                 sheet='Fuels',
                 lookup_var='fuelType'),
    'fossil fuel': dict(filepath='/Users/Tanzer/GitHub/BlackBlox/demoData/fuels.xlsx',
                 sheet='Fuels',
                 lookup_var='fossil fuel type'),
    'biofuel': dict(filepath='/Users/Tanzer/GitHub/BlackBlox/demoData/fuels.xlsx',
                 sheet='Fuels',
                 lookup_var='biofuel type'),
} 

my_default_units = {'mass': 'tonnes', 
                 'energy':'GJ',
}

input("\nPress enter to start demo\n")
print(f"\nBlackblox.py v0.2 Demonstration")
print(f"{datetime.now().strftime('%A, %d %B %Y at %H:%M')}")
print('\n')

dat.set_config(dat.filepaths, my_filepaths)
dat.set_config(dat.user_data, my_user_data)
dat.set_config(dat.lookup_var_dict, my_lookup_var_dict)
dat.set_config(dat.default_units, my_default_units)
print(f"Using unit process data from {dat.filepaths['unit_process_library_file']}")
print(f"and outputting data to {dat.filepaths['outdir']}")
print('\n')
    

###############################################################################
# UNIT PROCESS TEST
###############################################################################

# stop = input('UNIT PROCESS TEST - outputs to console. Press enter to proceed or type a character to skip: ')
# while stop == '':
#     stop = input("Press enter to balance a random unit or enter a character to skip: \n")
#     if stop != '':
#         break

#     unit_list =uni.df_unit_library.index.tolist()
#     random_unit = random.choice(unit_list)
#     random_unit = uni.UnitProcess(random_unit)
#     qty = round(random.uniform(10, 1000),2)
#     product = random_unit.default_product

#     scenarios = random_unit.var_df.index.tolist()
#     s = random.choice(scenarios)

#     print(str.upper(random_unit.name))
#     print("inflows:", random_unit.inflows)
#     print("outflows:", random_unit.outflows)
#     print(f"\nbalacing {random_unit.name} on {qty} of {product} ({random_unit.default_io}) using {s} values\n")

#     u_in, u_out = random_unit.balance(qty, scenario=s)
#     print("calculated inflow quantities:")
#     pprint(u_in)
#     print("\ncalculated outflow quantities:")
#     pprint(u_out)

#     stop = input(f"\nPress enter to balance {random_unit.name} on a random inflow: \n")
#     if stop != '':
#         break

#     print(f"\nselecting random inflow...")
#     product = random.choice(tuple(random_unit.inflows))
#     if product == 'fuel':
#             qty = u_in[random_unit.var_df.at[s, 'fuelType']]
#     else:
#         qty = u_in[product]
#     print(f"now balacing {random_unit.name} on {qty} of {product} ({'inflow'}) using {s} values\n")

#     u1_in, u1_out = random_unit.balance(qty, product, 'i', s) 
        
#     rounded_u_in = {k:round(v, 6) for k, v in u_in.items()}
#     rounded_u_out = {k:round(v, 6) for k, v in u_out.items()}
#     rounded_u1_in = {k:round(v, 6) for k, v in u1_in.items()}
#     rounded_u1_out = {k:round(v, 6) for k, v in u1_out.items()}
#     if rounded_u1_in == rounded_u_in and rounded_u1_out == rounded_u_out:
#         print("Same input/output as above, rounded to 6 decimal places")
#     else:
#         print("\n [!] not equivelent to above [!]\n")
#         print("recalculated inflow quantities:")
#         pprint(u1_in)
#         print("\ncalculated outflow quantities:")
#         pprint(u1_out)

#     stop = input(f"\nPress enter to test 1-to-1 recycle on {product}: \n")
#     if stop != '':
#         break

#     print(f"testing 1to1recycle on {product} (inflow)...")
    
#     qty_recycled = round(qty*random.uniform(0.01, 0.99),2)
#     max_replace_fraction = round(random.uniform(0.01, 1.0),2)
#     print(f"\nRecycling {qty_recycled} of RECYCLED FLOW 1-to1 for not more than {max_replace_fraction}% of {product}") 

#     r1_in, r1_out, leftover = random_unit.recycle_1to1(original_inflows_dict=u_in,
#                                                        original_outflows_dict=u_out,
#                                                        recycled_qty=qty_recycled,
#                                                        recycle_io='i',
#                                                        recycled_flow='RECYCLED FLOW',
#                                                        replaced_flow=product,
#                                                        max_replace_fraction=max_replace_fraction,
#                                                        scenario=s)
    
#     print("recalculated inflow quantities:")
#     pprint(r1_in)
#     rounded_r1_out = {k:round(v, 6) for k, v in r1_out.items()}
#     if rounded_r1_out == rounded_u_out:
#         print("Same outflow as above, rounded to 6 decimal places")
#     else:
#         print("\n [!] outflows not equivelent to above [!]\n")
#         print("recalculated outflow quantities:")
#         pprint(r1_out)
#     print(f"RECYCLE FLOW leftover: {leftover}\n")

#     if 'fuel' in random_unit.inflows:
#             fuel_type = random_unit.var_df.at[s, 'fuelType']
#             fuel_qty =  u_in[random_unit.var_df.at[s, 'fuelType']]
#             recycled_energy_qty = round(fuel_qty * random.uniform(30,100),2)
#             max_replace_fraction = round(random.uniform(0.01, 1.0),2)

#             print(f"\nalso testing recycle_energy_replacing_fuel on {fuel_type} (inflow)...")

#             print(f"\nRecycling {recycled_energy_qty} of RECYCLED ENERGY into {random_unit.name} replacing no more than {max_replace_fraction}% of {fuel_type})\n") 

#             r1_in, r1_out, leftover = random_unit.recycle_energy_replacing_fuel(original_inflows_dict=u_in,
#                                                                                 original_outflows_dict=u_out,
#                                                                                 recycled_qty=recycled_energy_qty,
#                                                                                 recycle_io="inflow",
#                                                                                 recycled_flow="RECYCLED ENERGY",
#                                                                                 replaced_flow=fuel_type,
#                                                                                 max_replace_fraction=max_replace_fraction,
#                                                                                 combustion_eff = dat.combustion_efficiency_var,
#                                                                                 scenario=s,
#                                                                                 emissions_list = dat.default_emissions)

#             print("recalculated inflow quantities:")
#             pprint(r1_in)
#             print("recalculated outflow quantities:")
#             pprint(r1_out)
#             print(f"RECYCLE FLOW leftover: {leftover}\n")
            

#     stop = input(f"\nPress enter to balance {random_unit.name} on a random outflow: \n")
#     if stop != '':
#         break

#     print(f"\nselecting random outflow...")
#     product = random.choice(tuple(random_unit.outflows))
#     if product == 'fuel':
#             qty = u_out[random_unit.var_df.at[s, 'fuelType']]
#     if product == 'slag':
#         print('cannot balance on slag, because slag is calculated as a remainder of an inflow and outflow. Skipping for now.')
#     else:
#         qty = u_out[product]
#         print(f"now balacing {random_unit.name} on {qty} of {product} ({'outflow'}) using {s} values\n")

#         u1_in, u1_out = random_unit.balance(qty, product, 'o', s) 
            
#         rounded_u1_in = {k:round(v, 6) for k, v in u1_in.items()}
#         rounded_u1_out = {k:round(v, 6) for k, v in u1_out.items()}
#         if rounded_u1_in == rounded_u_in and rounded_u1_out == rounded_u_out:
#             print("Same input/output as above, rounded to 6 decimal places")
#         else:
#             print("\n [!] not equivelent to above [!]\n")
#             print("calculated inflow quantities:")
#             pprint(u1_in)
#             print("\ncalculated outflow quantities:")
#             pprint(u1_out)
#             if product in dat.default_emissions or product == 'waste heat':
#                 print(f"\n(Since this was {product}, which has multiple sources, this was expected.)")

#         stop = input(f"\nPress enter to test 1-to-1 recycle on {product}: \n")
#         if stop != '':
#             break

#         print(f"\ntesting 1to1recycle on {product} (outflow)...")
#         qty_recycled = round(qty*random.uniform(1.1, 10),2)
#         max_replace_fraction = round(random.uniform(0.01, 1),2)
#         print(f"\nRecycling {qty_recycled} of RECYCLED FLOW 1-to1 for not more than {max_replace_fraction}% of {product}") 

#         r1_in, r1_out, leftover = random_unit.recycle_1to1(original_inflows_dict=u_in,
#                                                            original_outflows_dict=u_out,
#                                                            recycled_qty=qty_recycled,
#                                                            recycle_io='o',
#                                                            recycled_flow='RECYCLED FLOW',
#                                                            replaced_flow=product,
#                                                            max_replace_fraction=max_replace_fraction,
#                                                            scenario=s)

#         rounded_r1_in = {k:round(v, 6) for k, v in r1_in.items()}
#         if rounded_r1_in == rounded_u_in:
#             print("Same inflows as above, rounded to 6 decimal places")
#         else:
#             print("\n [!] inflows not equivelent to above [!]\n")
#             print("recalculated inflows quantities:")
#             pprint(r1_in)    
#         print("recalculated outflow quantities:")
#         pprint(r1_out)
#         print(f"RECYCLE FLOW leftover: {leftover}\n")

    
    
# print('\n')

###############################################################################
# PROCESS CHAIN TEST
###############################################################################
factory_file = "/Users/Tanzer/GitHub/BlackBlox/demoData/toy cement/cementFactory.xlsx"
df_cols = ['mixer', 'kiln', 'blender', 'chain totals']

stop = input('PROCESS CHAIN TEST - outputs to console. Press enter to proceed or type any character to skip: ')
while stop == '':
    if stop != '':
        break

    cement_chain = cha.ProductChain(chain_data=factory_file, 
                                    name= "Cement Production", 
                                    xls_sheet='Cement Chain')

    cement_chain.build()
    print('Cement Chain Data:')
    pprint(cement_chain.process_chain_df)

    stop = input("\nPress enter to generate CEMENT chain proces diagram: ")
    if stop != '':
        break
    cement_chain.diagram(view=True, save=False)

    stop = input("\nPress enter to balance the cement chain on 1.0 of cement out: ")
    if stop != '':
        break    

    chain_inflows, chain_outflows, int_flows, int_rows = cement_chain.balance(1.0)
    chain_inflows = pan.DataFrame(chain_inflows)
    chain_inflows = chain_inflows[df_cols]
    chain_outflows = pan.DataFrame(chain_outflows)
    chain_outflows = chain_outflows[df_cols]

    print("\n")
    print("cement chain inflows\n", chain_inflows, "\n")
    print("cement chain outflows\n", chain_outflows, "\n")

    print("cement chain intermediate flows")
    for row in int_rows:
        print(row)

    stop = input("\nPress enter to balance the cement chain on 1.070880 of CaCO3 in: ")
    if stop != '':
        break  
    inflows, outflows, int_flows, int_rows = cement_chain.balance(1.070880, product="CaCO3", scenario="default")
    inflows = pan.DataFrame(inflows)
    inflows = inflows[df_cols]

    outflows = pan.DataFrame(outflows)
    outflows = outflows[df_cols]

    print("cement chain inflows\n", inflows, "\n")
    print("cement chain outflows\n", outflows, "\n")

    stop = input("\nPress enter to balance the cement chain on 0.8 of clinker out of the kiln: ")
    if stop != '':
        break  

    inflows, outflows, int_flows, int_rows = cement_chain.balance(0.8, product="clinker", i_o='output', unit_process='kiln', scenario="default")
    inflows = pan.DataFrame(inflows)
    inflows = inflows[df_cols]
    outflows = pan.DataFrame(outflows)
    outflows = outflows[df_cols]

    print("\n")
    print("cement chain inflows\n", inflows, "\n")
    print("cement chain outflows\n", outflows, "\n")


    stop = 'stop'

###############################################################################
# FACTORY TEST
###############################################################################


# stop = input('INTERLINKED FACTORY TEST - outputs to console and file. Press enter to proceed or type any character to skip: ')
# while stop == '':
#     if stop != '':
#         break

#     cement_factory = fac.Factory(chain_list_file=factory_file,
#                                  chain_list_sheet='Chain List', 
#                                  connections_sheet='Connections', 
#                                  name="CementFactory")

#     print("\nname",cement_factory.name,"\n")
#     print("\nchain DF\n",cement_factory.chains_df)
#     print("\nconnections DF\n",cement_factory.connections_df)

#     cement_factory.diagram()

#     cement_factory.build()

#     print("\nchain dict:",cement_factory.chain_dict)
#     print("\nmain chain:",cement_factory.chain_dict[cement_factory.main_chain])

#     inflows, outflows = cement_factory.balance(1.0, scenario='default', write_to_xls=True)

#     totals = {'factory inflows': inflows, 'factory outflows': outflows}
#     print(pan.DataFrame(totals), "\n")




###############################################################################
# INDUSTRY TEST
###############################################################################

# stop = input('INDUSTRY TEST - outputs to file. Press enter or type a character to skip: ')
# while stop == '':
#     stop = input("Press enter to balance the entire cement industry or enter a character to skip: \n")
#     if stop != '':
#         break

#     i_kwargs = dict(factory_list_file='excelData/cementIndustry.xlsx',
#                     factory_list_sheet='Factory List', 
#                     connections_sheet='Factory Connections', 
#                     name='Cement Industry')

#     industry = Industry(**i_kwargs)

#     industry.build()

#     for factory, details in industry.factory_dict.items():
#         print(factory, details)

#     ioDicts= industry.balance(products_sheet='1990-Absolute', write_to_xls=True, 
#                     file_id='1990-Absolute', diagrams=True)


#     ioDicts= industry.balance(products_sheet='2010-Relative', write_to_xls=True, 
#                     file_id='2010-Relative', diagrams=True)

#     ioDicts= industry.balance(products_sheet='2010-Relative', write_to_xls=True, 
#                     file_id='2010-Relative-default', force_scenario='default', diagrams=True)

#     s_list = ['default', 'EU-typ', 'EU-bat']

#     s_kwargs = dict(scenario_list=s_list, 
#                     products_sheet='1990-Relative', 
#                     write_to_xls=True, 
#                     file_id='1990-Relative', 
#                     diagrams=False)

#     industry.run_scenarios(**s_kwargs)

#     e_kwargs = dict(start_sheet='1990-Absolute', 
#                     end_sheet='2010-Absolute',
#                     start_step=1990,
#                     end_step=2010,
#                     write_to_xls=True, 
#                     diagrams=True,
#                     graph_outflows = ['CO2', 'cement'])
#     industry.evolve(**e_kwargs)
