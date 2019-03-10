import random
from pprint import pprint
from datetime import datetime

import dataconfig as dat
import unitprocess as uni
import processchain as cha


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


input("\nPress enter to start demo\n")
print(f"\nBlackblox.py v0.2 Demonstration")
print(f"{datetime.now().strftime('%A, %d %B %Y at %H:%M')}")
print('\n')

dat.set_config(dat.filepaths, my_filepaths)
dat.set_config(dat.user_data, my_user_data)
dat.set_config(dat.lookup_var_dict, my_lookup_var_dict)
print(f"Using unit process data from {dat.filepaths['unit_process_library_file']}")
print(f"and outputting data to {dat.filepaths['outdir']}")
print('\n')
    

###############################################################################
# UNIT PROCESS TEST
###############################################################################

stop = input('UNIT PROCESS TEST - outputs to console. Press enter to proceed or type a character to skip: ')
while stop == '':
    stop = input("Press enter to balance a random unit or enter a character to skip: \n")
    if stop != '':
        break

    unit_list =uni.df_unit_library.index.tolist()
    random_unit = random.choice(unit_list)
    random_unit = uni.UnitProcess(random_unit)
    qty = round(random.uniform(10, 1000),2)
    product = random_unit.default_product

    scenarios = random_unit.var_df.index.tolist()
    s = random.choice(scenarios)

    print(str.upper(random_unit.name))
    print("inflows:", random_unit.inflows)
    print("outflows:", random_unit.outflows)
    print(f"\nbalacing {random_unit.name} on {qty} of {product} ({random_unit.default_io}) using {s} values\n")

    u_in, u_out = random_unit.balance(qty, scenario=s)
    print("calculated inflow quantities:")
    pprint(u_in)
    print("\ncalculated outflow quantities:")
    pprint(u_out)

    stop = input(f"\nPress enter to balance {random_unit.name} on a random inflow: \n")
    if stop != '':
        break

    print(f"\nselecting random inflow...")
    product = random.choice(tuple(random_unit.inflows))
    if product == 'fuel':
            qty = u_in[random_unit.var_df.at[s, 'fuelType']]
    else:
        qty = u_in[product]
    print(f"now balacing {random_unit.name} on {qty} of {product} ({'inflow'}) using {s} values\n")

    u1_in, u1_out = random_unit.balance(qty, product, 'i', s) 
        
    rounded_u_in = {k:round(v, 6) for k, v in u_in.items()}
    rounded_u_out = {k:round(v, 6) for k, v in u_out.items()}
    rounded_u1_in = {k:round(v, 6) for k, v in u1_in.items()}
    rounded_u1_out = {k:round(v, 6) for k, v in u1_out.items()}
    if rounded_u1_in == rounded_u_in and rounded_u1_out == rounded_u_out:
        print("Same input/output as above, rounded to 6 decimal places")
    else:
        print("\n [!] not equivelent to above [!]\n")
        print("recalculated inflow quantities:")
        pprint(u1_in)
        print("\ncalculated outflow quantities:")
        pprint(u1_out)

    stop = input(f"\nPress enter to test 1-to-1 recycle on {product}: \n")
    if stop != '':
        break

    print(f"testing 1to1recycle on {product} (inflow)...")
    
    qty_recycled = round(qty*random.uniform(0.01, 0.99),2)
    max_replace_fraction = round(random.uniform(0.01, 1.0),2)
    print(f"\nRecycling {qty_recycled} of RECYCLED FLOW 1-to1 for not more than {max_replace_fraction}% of {product}") 

    r1_in, r1_out, leftover = random_unit.recycle_1to1(original_inflows_dict=u_in,
                                                       original_outflows_dict=u_out,
                                                       recycled_qty=qty_recycled,
                                                       recycle_io='i',
                                                       recycled_flow='RECYCLED FLOW',
                                                       replaced_flow=product,
                                                       max_replace_fraction=max_replace_fraction,
                                                       scenario=s)
    
    print("recalculated inflow quantities:")
    pprint(r1_in)
    rounded_r1_out = {k:round(v, 6) for k, v in r1_out.items()}
    if rounded_r1_out == rounded_u_out:
        print("Same outflow as above, rounded to 6 decimal places")
    else:
        print("\n [!] outflows not equivelent to above [!]\n")
        print("recalculated outflow quantities:")
        pprint(r1_out)
    print(f"RECYCLE FLOW leftover: {leftover}\n")

    if 'fuel' in random_unit.inflows:
            fuel_type = random_unit.var_df.at[s, 'fuelType']
            fuel_qty =  u_in[random_unit.var_df.at[s, 'fuelType']]
            recycled_energy_qty = round(fuel_qty * random.uniform(30,100),2)
            max_replace_fraction = round(random.uniform(0.01, 1.0),2)

            print(f"\nalso testing recycle_energy_replacing_fuel on {fuel_type} (inflow)...")

            print(f"\nRecycling {recycled_energy_qty} of RECYCLED ENERGY into {random_unit.name} replacing no more than {max_replace_fraction}% of {fuel_type})\n") 

            r1_in, r1_out, leftover = random_unit.recycle_energy_replacing_fuel(original_inflows_dict=u_in,
                                                                                original_outflows_dict=u_out,
                                                                                recycled_qty=recycled_energy_qty,
                                                                                recycle_io="inflow",
                                                                                recycled_flow="RECYCLED ENERGY",
                                                                                replaced_flow=fuel_type,
                                                                                max_replace_fraction=max_replace_fraction,
                                                                                combustion_eff = dat.combustion_efficiency_var,
                                                                                scenario=s,
                                                                                emissions_list = dat.default_emissions)

            print("recalculated inflow quantities:")
            pprint(r1_in)
            print("recalculated outflow quantities:")
            pprint(r1_out)
            print(f"RECYCLE FLOW leftover: {leftover}\n")
            

    stop = input(f"\nPress enter to balance {random_unit.name} on a random outflow: \n")
    if stop != '':
        break

    print(f"\nselecting random outflow...")
    product = random.choice(tuple(random_unit.outflows))
    if product == 'fuel':
            qty = u_out[random_unit.var_df.at[s, 'fuelType']]
    if product == 'slag':
        print('cannot balance on slag, because slag is calculated as a remainder of an inflow and outflow. Skipping for now.')
    else:
        qty = u_out[product]
        print(f"now balacing {random_unit.name} on {qty} of {product} ({'outflow'}) using {s} values\n")

        u1_in, u1_out = random_unit.balance(qty, product, 'o', s) 
            
        rounded_u1_in = {k:round(v, 6) for k, v in u1_in.items()}
        rounded_u1_out = {k:round(v, 6) for k, v in u1_out.items()}
        if rounded_u1_in == rounded_u_in and rounded_u1_out == rounded_u_out:
            print("Same input/output as above, rounded to 6 decimal places")
        else:
            print("\n [!] not equivelent to above [!]\n")
            print("calculated inflow quantities:")
            pprint(u1_in)
            print("\ncalculated outflow quantities:")
            pprint(u1_out)
            if product in dat.default_emissions or product == 'waste heat':
                print(f"\n(Since this was {product}, which has multiple sources, this was expected.)")

        stop = input(f"\nPress enter to test 1-to-1 recycle on {product}: \n")
        if stop != '':
            break

        print(f"\ntesting 1to1recycle on {product} (outflow)...")
        qty_recycled = round(qty*random.uniform(1.1, 10),2)
        max_replace_fraction = round(random.uniform(0.01, 1),2)
        print(f"\nRecycling {qty_recycled} of RECYCLED FLOW 1-to1 for not more than {max_replace_fraction}% of {product}") 

        r1_in, r1_out, leftover = random_unit.recycle_1to1(original_inflows_dict=u_in,
                                                           original_outflows_dict=u_out,
                                                           recycled_qty=qty_recycled,
                                                           recycle_io='o',
                                                           recycled_flow='RECYCLED FLOW',
                                                           replaced_flow=product,
                                                           max_replace_fraction=max_replace_fraction,
                                                           scenario=s)

        rounded_r1_in = {k:round(v, 6) for k, v in r1_in.items()}
        if rounded_r1_in == rounded_u_in:
            print("Same inflows as above, rounded to 6 decimal places")
        else:
            print("\n [!] inflows not equivelent to above [!]\n")
            print("recalculated inflows quantities:")
            pprint(r1_in)    
        print("recalculated outflow quantities:")
        pprint(r1_out)
        print(f"RECYCLE FLOW leftover: {leftover}\n")

    
    
print('\n')

###############################################################################
# PROCESS CHAIN TEST
###############################################################################
chain_file_dict = {'cement': ,
                    'power': ,
                    'CO2 capture': }


stop = input('PROCESS CHAIN TEST - outputs to console. Press enter to proceed or type any character to skip: ')
while stop == '':
    stop = input("Press enter to [re]balance the CEMENT chain or enter a character to skip: \n")
    if stop != '':
        break

    cement_chain = cha.ProductChain(flowTSV, "cement production")

###############################################################################
# FACTORY TEST
###############################################################################


stop = input('FACTORY TEST - outputs to file. Press enter or type a character to skip: ')
while stop == '':
    stop = input("Press enter to balance a random factory or enter a character to skip: \n")
    if stop != '':
        break

###############################################################################
# INDUSTRY TEST
###############################################################################

stop = input('INDUSTRY TEST - outputs to file. Press enter or type a character to skip: ')
while stop == '':
    stop = input("Press enter to balance the entire cement industry or enter a character to skip: \n")
    if stop != '':
        break