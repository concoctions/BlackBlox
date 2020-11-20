import random
import pandas as pan
from pprint import pprint
from datetime import datetime

import blackblox.io_functions as iof
import blackblox.dataconfig as dat
import blackblox.unitprocess as uni
import blackblox.processchain as cha
import blackblox.factory as fac
import blackblox.industry as ind

factory_file = "data/demo/factories/cementFactory_withCCS.xlsx"
scenario_list = ['EU-1990', 'EU-2000', 'EU-2010']


# USER DATA CONFIG
dat.outdir = 'output/demo'
dat.user_data = {"name": "S.E. Tanzer",
             "affiliation": "TU Delft",
             "project": f"BlackBlox Demo - {datetime.now().strftime('%d %B %Y')}",
}

dat.default_units = {'mass': 'tonnes', 
                 'energy':'GJ',
}

dat.default_emissions = ['CO2__fossil']
print("\n\nWELCOME\n\n")

print(f"\n\nblackblox.py v0.1 Demonstration")
print(f"{datetime.now().strftime('%A, %d %B %Y at %H:%M')}")

print(f"\nThis demo uses unit process data from {dat.unit_process_library_file}")
print(f"and outputting any files to {dat.outdir}")

# input("\nPress enter to start demo: ") 

# #############################################################################
# # UNIT PROCESS TEST
# #############################################################################
# print('\n\n\nUNIT PROCESS TEST - outputs to console.')
# print("\nA UNIT PROCESS is the basic building block of blackblox.")
# print('It represents a single "black box" process with a set of inflows and outflows.')

# stop = input("\nPress enter to create the KILN unit process: ")

# unit_list =uni.df_unit_library.index.tolist()
# kiln = uni.UnitProcess('demo_kiln')

# print(f"\n{str.upper(kiln.name)}")
# print("inflows:", ', '.join(kiln.inflows))
# print("outflows:", ', '.join(kiln.outflows))

# # BALANCE UNIT PROCESS 
# print("\n\nUnit Processes are balanced using a table of CALCULATIONS and a table of VARIABLES.")
# print("CALCULATION tables contain a set of relationships between the flows of the unit process.")
# print("\nE.g.:\n")
# print(kiln.calc_df.iloc[0])
# print("\n The VARIABLES table contains the numeric ratios and other data that are necessary")
# print("to complete the calculations. E.g.:\n")
# print(kiln.var_df.loc['EU-2010'])
# print("\nTHE VARIALBES table is kep separate from the CALCULATIONS")
# print("so to allow for multiple configurationsto be easily tested.\n\n")

# stop = input("\nPress enter to balance the KILN unit process: ")
# qty = 1.0 # round(random.uniform(10, 1000),2)
# product = kiln.default_product

# scenarios = kiln.var_df.index.tolist()
# s = 'EU-2010' # random.choice(scenarios)

# u_in, u_out = kiln.balance(qty, scenario=s, write_to_console=True)

#     # stop = True

# stop = input("\nPress enter to continue\n")

# # BALANCE UNIT PROCESS - Random Inflow
# print("\nThere must be sufficient calculations that there remain zero degrees of freedom")
# print("That is, that by providing the quantity of any inflow or outflow (besides wastes)")
# print("all the remaining flows are calculable.")

# stop = input(f"\n\nPress enter to balance {kiln.name} on a random inflow: ")

# print(f"\nselecting random inflow...")
# product = random.choice(tuple(kiln.inflows))
# if product == 'fuel':
#         qty = u_in[kiln.var_df.at[s, 'fueltype']]
# else:
#     qty = u_in[product]
# print(f"\nnow balacing {kiln.name} on {qty} {dat.default_units['mass']} of {product} ({'inflow'}) using {s} values")

# u1_in, u1_out = kiln.balance(qty, product, 'i', s, write_to_console=True) 
    
# rounded_u_in = {k:round(v, dat.float_tol) for k, v in u_in.items()}
# rounded_u_out = {k:round(v, dat.float_tol) for k, v in u_out.items()}
# rounded_u1_in = {k:round(v, dat.float_tol) for k, v in u1_in.items()}
# rounded_u1_out = {k:round(v, dat.float_tol) for k, v in u1_out.items()}
# if rounded_u1_in == rounded_u_in and rounded_u1_out == rounded_u_out:
#     print(f"\nSame input/output as above, rounded to {dat.float_tol} decimal places")
# else:
#     print("\n [!] Rebalanced input/output not equivelent to above [!]\n")


# # BALANCE UNIT PROCESS - Recycle inflow  
# print("It is possible to substitute calculated flows, wholly or partly with")
# print("another specified flow. This is one way unit processes can be connected")
# print("with one another.")

# stop = input(f"\nPress enter to test 1-to-1 recycle on {product} (inflow): ")

# qty_recycled = 5.0 # round(qty*random.uniform(0.01, 0.99),2)
# max_replace_fraction = 0.5 #round(random.uniform(0.01, 1.0),2)
# print(f"\nRecycling {qty_recycled} of RECYCLED FLOW 1-to-1 for not more than {max_replace_fraction*100}% of {product}") 

# r1_in, r1_out, leftover = kiln.recycle_1to1(original_inflows_dict=u_in,
#                                                     original_outflows_dict=u_out,
#                                                     recycled_qty=qty_recycled,
#                                                     recycle_io='i',
#                                                     recyclate_flow='RECYCLED FLOW',
#                                                     toBeReplaced_flow=product,
#                                                     max_replace_fraction=max_replace_fraction,
#                                                     scenario=s,
#                                                     write_to_console=True)


# rounded_r1_out = {k:round(v, dat.float_tol) for k, v in r1_out.items()}
# if rounded_r1_out == rounded_u_out:
#     print(f"\nSame input/output as above, rounded to {dat.float_tol} decimal places")
# else:
#     print("\n [!] Rebalanced input/output not equivelent to above [!]\n")
# print(f"\nRECYCLE FLOW leftover: {leftover}")

# stop = input("\nPress enter to continue\n")

# # ENERGY REPLACING FUEL 


# fuel_type = kiln.var_df.at[s, 'fueltype']
# fuel_qty =  u_in[kiln.var_df.at[s, 'fueltype']]
# recycled_energy_qty = 4.0 #round(fuel_qty * random.uniform(30,100),2)
# max_replace_fraction = 0.5 #round(random.uniform(0.01, 1.0),2)


# print("One recycling option is to replace energy generated by fuel in a unit process")
# print("by energy generated somewhere else. In this case, the quantity of fuel and")
# print("any combustion emissions are recalculated as well.")

# stop = input(f"\n\n\nPress enter to recycle energy to replace {fuel_type} (inflow) in  {kiln.name}")

# print(f"\nRecycling {recycled_energy_qty} {dat.default_units['energy']} of RECYCLED ENERGY into {kiln.name} replacing no more than {max_replace_fraction*100}% of {fuel_type})") 

# r1_in, r1_out, leftover = kiln.recycle_energy_replacing_fuel(original_inflows_dict=u_in,
#                                                                     original_outflows_dict=u_out,
#                                                                     recycled_qty=recycled_energy_qty,
#                                                                     recycle_io="inflow",
#                                                                     recyclate_flow="RECYCLED ENERGY",
#                                                                     toBeReplaced_flow=fuel_type,
#                                                                     max_replace_fraction=max_replace_fraction,
#                                                                     combustion_eff = dat.combustion_efficiency_var,
#                                                                     scenario=s,
#                                                                     emissions_list = dat.default_emissions,
#                                                                     write_to_console=True)


# print(f"\nRECYCLE FLOW leftover: {leftover}")
# stop = input("\nPress enter to continue\n")

# #BALANCE UNIT PROCESS - run scenarios 

# print("It is also possible to run multiple sets of variables at once")
# print("for ease of comparison.")
# stop = input(f"\n\n\nPress enter to test unit process multiple scenarios: ")

# kiln.run_scenarios(scenario_list=scenario_list,write_to_console=True)
    
# stop = input("\nPress enter to continue\n") 

# #############################################################################
# # PROCESS CHAIN TEST
# #############################################################################

# print("\n\n\nPROCESS CHAIN TEST - outputs to console and file. \n")

# print("Unit processes can be connected linearly into PROCESS CHAINS.")
# print("In a CHAIN, an outflow of a unit process is an inflow of another unit process.")
# print("A CHAIN can be balanced on any flow in any unit process in the CHAIN")
# print("Inflows and outflows are calculated for each unit and the overall chain.")

# stop = input('\nPress enter to create a CEMENT production chain object: ')

# cement_chain = cha.ProductChain(chain_data=factory_file, 
#                                 name= "Cement", 
#                                 xls_sheet='Cement Chain')


# print('\nCEMENT Chain Data:')
# pprint(cement_chain.process_chain_df)

# stop = input("\n\n\nPress enter to generate CEMENT chain proces diagram: ")
# cement_chain.diagram(view=True, save=False)
# print("\nDiagram sent to system viewer.")

# stop = input("\n\n\nPress enter to balance the cement chain on 1.0 tonnes of cement out: ")

# chain_inflows, chain_outflows, int_flows, int_rows = cement_chain.balance(1.0, write_to_console=True)

# stop = input("\n\n\nPress enter to balance the cement chain on 1.070880 of CaCO3 in: ")
# inflows, outflows, int_flows, int_rows = cement_chain.balance(1.070880, product="CaCO3", scenario="default", write_to_console=True)

# stop = input("\n\n\nPress enter to balance the cement chain on 0.8 of clinker out of the kiln: ")

# inflows, outflows, int_flows, int_rows = cement_chain.balance(0.8, product="clinker", i_o='outflow', unit_process='demo_kiln', scenario="default", write_to_console=True)

# stop = input(f"\n\n\nPress enter to balance the cement chain on 1.0 of cement out for scenarios {scenario_list} ") 

# cement_chain.run_scenarios(scenario_list=scenario_list,write_to_console=True, write_to_xls=True)

# stop = 'stop'

# input('\n\n\nPress enter to continue: ')  

# ##############################################################################
# ## FACTORY TEST
# # ##############################################################################
# print('\n\n\nINTERLINKED FACTORY TEST - outputs to console and file.')
# print("A FACTORY can contain multiple chains, linked at any process in the chain")
# print("Flows from one unit process can be be recycled within the factory.")

# stop = input('\nPress enter to create a CEMENT factory object: ')

# cement_factory = fac.Factory(chain_list_file=factory_file,
#                                 chain_list_sheet='Chain List', 
#                                 connections_sheet='Connections', 
#                                 name="Demo")

# print(f"\n{cement_factory.name} factory")
# print(f"\nchains in this factory:")
# for chain in cement_factory.chain_dict:
#     print(cement_factory.chain_dict[chain]['name'])

# print("\n connections in this factory:")
# print(cement_factory.connections_df[[dat.origin_chain, dat.origin_unit, dat.origin_product, \
#     dat.dest_unit, dat.dest_chain, dat.replace]])

# stop = input("\n\n\nPress enter to see all connection data for waste heat recycling: ")
# print("\n",cement_factory.connections_df.iloc[3, :])

# stop = input("\n\n\nPress enter to generate a diagram of the cement factory: ")
# cement_factory.diagram(view=True, save=False)
# print("\nDiagram sent to system viewer.")

# stop = input("\n\n\nPress enter to balance the factory on 100.0 tonnes of cement (outputs to file): ")
# inflows, outflows, agg, net = cement_factory.balance(product_qty = 100, 
#                                             scenario=dat.default_scenario, 
#                                             write_to_xls=False)

# totals = {'factory inflows': inflows, 'factory outflows': outflows}
# totals = pan.DataFrame(totals)
# totals = iof.mass_energy_df(totals)
# print(f"\n{cement_factory.name} total inflows and outflows")
# print(totals)
# print(f"\n Full results available in {dat.outdir} directory.")


# stop = input("\n\n\nPress enter to balance the factory on 13.9535 tonnes of fuel inflow to kiln (outputs to file): ")
# inflows, outflows, agg, net = cement_factory.balance(product_qty = 13.9535, 
#                                             product = 'fuel',
#                                             product_io = 'inflow',
#                                             product_unit = 'demo_kiln',
#                                             scenario=dat.default_scenario, 
#                                             write_to_xls=True)

# totals = {'factory inflows': inflows, 'factory outflows': outflows}
# totals = pan.DataFrame(totals)
# totals = iof.mass_energy_df(totals)

# print(f"\n{cement_factory.name} total inflows and outflows")
# print(totals, "\n")
# print(f"\n Full results available in {dat.outdir} directory")


###############################################################################
## INDUSTRY TEST  - NOT UPDATED AT REFACTOR
###############################################################################
# input('\n\n\nPress enter to continue: ') 

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
            
    print(f"\nDone. Files available in {dat.outdir} directory.")

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

    print(f"\nDone. Files available in {dat.outdir} directory.")

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

    print(f"Done. Files available in {dat.outdir} directory.")

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

    print(f"\nDone. Files available in {dat.outdir} directory.")
    stop = 'stop'

input("\n\n\nPress enter to end demo. \n")

print('\n\n\nGOOD BYE.\n\n')