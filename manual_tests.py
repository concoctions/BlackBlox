# IMPORT MODULES
from molmass import Formula
from collections import defaultdict
from copy import copy
import pandas as pan
import os
import logging
import sys
import random

# import other BlackBlox modules
from dataconfig import *
from custom_lookup import *
from unitprocess import *
from processchain import *
from factory import *
from industry import *
from molmass import Formula
from bb_log import get_logger
from calculators import *

logger = get_logger("testing")

#specify number of test runs
runs = 3

logger.info(f"\n\n\nRunning new test with {runs} runs")

print_startup = False
test_calculators = False
test_unitprocesses = True
test_chains = False
test_factory = False
test_industry = False


if print_startup is True:
    print("\ninititalizing test of refactored blackblox.py\n")

    print("unitlist:")
    print(df_unit_library,'\n')

    print("fuel list:")
    print(df_fuels,'\n')


###                                                                          ###
################################################################################
###  CALCULATOR TESTS  #########################################################
################################################################################
###                                                                          ###
if test_calculators is True:
    print("\nTesting calculation classes")

    print("\nRatio Test")
    known = 'A'
    unknown = 'B'

    for i in range(runs):
        knownQty = random.uniform(0.001,1000)
        ratio = random.uniform(1,100)
        unknownQty = knownQty * ratio

        print("\nusing:\nknown:", known, ", qty:", knownQty, \
        "\nunknown", unknown, ", qty:", unknownQty, \
        "\nratio (mass)", ratio,'\n')

        ratioTest = Ratio(knownQty, ratio)
        if round(ratioTest,5) == round(unknownQty,5):
            print("correctly solved for", unknown, ratioTest)
        else:
            print("ERROR:", ratioTest, "!=", unknownQty)
            sys.exit("Something went wrong")

        ratioTest_i = Ratio(unknownQty, ratio, invert = True)
        if round(ratioTest_i,5) == round(knownQty,5):
            print("correctly solved with inversion for:", unknown, ratioTest_i)
        else:
            print("ERROR:", ratioTest_i, "!=", knownQty)
            sys.exit("Something went wrong")

    print("\nRemainder Test")
    known = 'A'
    unknown = 'B'


    for i in range(runs):

        knownQty = random.uniform(0.001,1000)
        ratio = random.random()
        unknownQty = knownQty * (1 - ratio)
        print("\nusing:\nknown:", known, ", qty:", knownQty, \
        "\nunknown", unknown, ', qty:', unknownQty, \
        "\ngiven ratio", ratio, \
        "\nderived remainder ratio", (1 - ratio), '\n')

        remainderTest = Remainder(knownQty, ratio)
        if round(remainderTest,5) == round(unknownQty,5):
            print("correctly solved for:", unknown, remainderTest)
        else:
            print("ERROR:", remainderTest, "!=", unknownQty)
            sys.exit("Something went wrong")

        remainderTest_i = Remainder(unknownQty, ratio, invert=True)
        if round(remainderTest_i,5) == round(knownQty,5):
            print("correctly solved for:", unknown, remainderTest_i)
        else:
            print("ERROR:", remainderTest_i, "!=", knownQty)
            sys.exit("Something went wrong")

    print("\nMolMassRatio Test")
    molecules = ['H2', 'H2O', 'C2O', 'NH4', 'NH3', 'CaCO3', 'CaO'\
    'C9H8O4', 'Si', 'NaC18H35O2', 'H2SO4', 'C2H6O', '[2H]2O', '(COOH)2',\
    'D2O', 'C48H32AgCuO12P2Ru4', 'CH3COOH', 'SO2', 'NaHCO3', 'NaCl', \
    'NaOH', 'Na2[B4O5(OH)4].5H2O']

    for i in range(runs):
        known = random.choice(molecules)
        knownQty = random.uniform(0.001, 1000)
        unknown = random.choice(molecules)
        unknownQty = (Formula(unknown).mass / Formula(known).mass) * knownQty

        print("using:\nknown:", known, ", qty:", knownQty, \
        "\nunknown", unknown, ", qty:", unknownQty, \
        "\nratio (mass)", Formula(unknown).mass / Formula(known).mass,'\n')

        molRatioTest = MolMassRatio(known, knownQty, unknown)
        if round(molRatioTest,5) == round(unknownQty, 5):
            print("correctly solved for:", unknown, molRatioTest)
        else:
            print("ERROR:", molRatioTest, "!=", round(unknownQty, 5))
            sys.exit("Something went wrong")      


    print("\nCombustion Test")
    fuels = df_fuels.index.tolist()


    for i in range(runs):
        known = random.choice(fuels)
        knownQty = random.uniform(0.001, 1000)
        unknown = 'heat MJs'
        combustEff = random.random()
        unknownQty = knownQty * df_fuels.at[known, 'HHV'] * combustEff
        emissionsDict = defaultdict(float)

        print("\nusing:\nknown:", known, ", qty:", knownQty, \
        "\nunknown;", unknown, ", qty:", unknownQty, \
        "\nCombustEff;", combustEff,'\n')

        combustTest1 = Combustion(known, knownQty, unknown, combustEff)
        if round(combustTest1, 5) == round(unknownQty, 5):
            print("correctly solved for:", unknown, combustTest1)
        else:
            print("ERROR:", combustTest1, "!=", unknownQty)
            sys.exit("Something went wrong") 

        combustTest2 = Combustion(unknown, unknownQty, known, combustEff, emissionsDict)
        if round(combustTest2, 5) == round(knownQty, 5):
            print("correctly solved for:", known, combustTest2)
            print("and wrote emissions to dictionary:", emissionsDict)
        else:
            print("ERROR:", combustTest2, "!=", knownQty)
            sys.exit("Something went wrong")

###                                                                          ###
################################################################################
###  UNIT PROCESS TESTS  #######################################################
################################################################################
###                                                                          ###

if test_unitprocesses is True:
    print("\nUnit Process Test")

    units =df_unit_library.index.tolist()

    for i in range(runs):
        name = random.choice(units)
        # product = df_unit_processes.at[name, default_product_col]
        # i_o = df_unit_processes.at[name, default_product_io_col]
        qty = random.uniform(0.001, 1000)

        unit1 = UnitProcess(name)

        scenarios = unit1.var_df.index.tolist()
        s = random.choice(scenarios)

        print("\nUsing:", unit1.name, unit1.default_product, qty, unit1.default_io, s)

        print(unit1.name, "inflows:", unit1.inflows)
        print(unit1.name, "outflows:", unit1.outflows)

        u_in, u_out = unit1.balance(qty, var_i=s)
        print(u_in)
        print(u_out)

    # Test for random input
        product = random.choice(tuple(unit1.inflows))
        # while (product == 'fuel' and len(unit1.inflows) > 1):   #fuel combustion calcs writes CO2 to output in balance; this can mess up numbers if there's something else that writes to CO2. fix this later.
        #     product = random.choice(tuple(unit1.inflows))
        qty = u_in[product]

        if product == 'fuel':
            qty = u_in[unit1.var_df.at[s, 'fuelType']]

        i_o = "IN"

        print("\nUsing:",\
        name, product, i_o, qty, s)
        
        u1_in, u1_out = unit1.balance(qty, product, i_o, s) 

        if u1_in == u_in and u1_out == u_out:
            print("Same input/output as above")
        else:
            print("not equivelent to above")
            print(u1_in)
            print(u1_out)

        # Test for 1-to-1 recycle
        qty_recycled = qty*random.uniform(0.1, 0.9)
        print(f"\nRecycling of {qty_recycled} RECYCLE 1-to-1 into {unit1.name} for {product}") 

        r1_in, r1_out, leftover = unit1.recycle_1to1(u1_in, u1_out, qty_recycled, i_o,
                                  "RECYCLE", product, var_i=s)

        print(r1_in)
        print(r1_out)
        print(f"RECYCLE leftover: {leftover}\n")

        qty_recycled = qty*random.uniform(1, 10)
        print(f"\nRecycling of {qty_recycled} RECYCLE 1-to-1 into {unit1.name} for {product}") 

        r1_in, r1_out, leftover = unit1.recycle_1to1(u1_in, u1_out, qty_recycled, i_o,
                                  "RECYCLE", product)

        print(r1_in)
        print(r1_out)
        print(f"RECYCLE leftover: {leftover}\n")


    # Test for random output
        product = random.choice(tuple(unit1.outflows))
        
        qty = u_out[product]
        
        if product == 'fuel':
            qty = u_out[unit1.var_df.at[s, 'fuelType']]
        
        i_o = "Out!"


        print("\nUsing:",\
        name, product, i_o, qty, s)
        
        u1_in, u1_out = unit1.balance(qty, product, i_o, s) 

        if u1_in == u_in and u1_out == u_out:
            print("Same input/output as above")
        else:
            print("not equivelent to above")
            print(u1_in)
            print(u1_out)

    #Test for fuel substition

    # kiln = UnitProcess('kiln')
    # qty = random.uniform(0.1, 1000)
    # k1_in, k1_out = kiln.balance(qty, 'clinker')

    print("\ntesting energy recycle\n")
    power = UnitProcess('PowerStation')
    qty = random.uniform(0.1, 1000)
    p1_in, p1_out = power.balance(qty, 'electricity')
    
    print(power.name)
    print(p1_in)
    print(p1_out)

    e_qty= p1_out['electricity']* random.uniform(0.1, 0.9)
    print(f"\nRecycling of {e_qty} RECYCLED ENERGY into {power.name} for fuel replacement (equal to {e_qty/33.7/0.8} of coal)") 
    r2_in, r2_out, r2_leftover = power.recycle_energy_replacing_fuel(
                                 p1_in, p1_out, 
                                 e_qty, 'INFLOW', "RECYCLED ENERGY",
                                 'fuel', 'combustEff')

    print(r2_in)
    print(r2_out)
    print(f"RECYCLE leftover: {r2_leftover}\n")
    
    print(f"check for O2/CO2 emissions only..balancing PowerStation on {r2_in['coal']} of coal")
    c2_in, c2_out = power.balance(r2_in['coal'], 'fuel', i_o='in')
    print(c2_in)
    print(c2_out)


    print("\n",power.name)
    print(p1_in)
    print(p1_out)
    e_qty= p1_out['electricity']* random.uniform(2, 10)
    print(f"\nRecycling of {e_qty} RECYCLED ENERGY into {power.name} for fuel replacement (equal to {e_qty/33.7/0.8} of coal)") 
    r3_in, r3_out, r3_leftover = power.recycle_energy_replacing_fuel(
                                 p1_in, p1_out, 
                                 e_qty, 'INFLOW', "RECYCLED ENERGY",
                                 'fuel', 'combustEff')
    print(r3_in)
    print(r3_out)
    print(f"RECYCLE leftover: {r3_leftover}\n")



###                                                                          ###
################################################################################
###  LINEAR CHAIN TESTS  #######################################################
################################################################################
###                                                                          ###

if test_chains is True:
    print("\nChain Test\n")

    flowTSV = "chainFiles/cementFlow.tsv"

    chain = ProductChain(flowTSV, "cement production")

    print(chain.name)
    print(chain.process_chain_df)
    print(chain.process_list)

    chain.build()
    print(chain.process_list)

    inflows, outflows = chain.balance(1.0, var_i="default")

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    inflows, outflows = chain.balance(0.452447, product="CaCO3", var_i="EU-bat")

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    inflows, outflows = chain.balance(0.174018, product="clay", var_i="EU-bat")

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    chain.diagram()


    flowTSV = "chainFiles/CO2CapFlow.tsv"

    chain = ProductChain(flowTSV, "CO2 capture")

    print(chain.name)
    print(chain.process_chain_df)
    print(chain.process_list)


    inflows, outflows = chain.balance(0.744351, product="CO2", i_o="i", var_i='default')

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    inflows, outflows = chain.balance(1.0, product="compressedCO2", var_i="EU-bat")

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    inflows, outflows = chain.balance(0.174018, product="CO2", var_i="EU-bat")

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    chain.diagram()

    flowTSV = "chainFiles/powerFlow.tsv"

    chain = ProductChain(flowTSV, "Electricity Generation")

    print(chain.name)
    print(chain.process_chain_df)
    print(chain.process_list)

    inflows, outflows = chain.balance(1.0)

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    inflows, outflows = chain.balance(180.093237, product="electricity", var_i="default")

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    inflows, outflows = chain.balance(0.174018, product="fuel", var_i="EU-old")

    print("inputs\n", pan.DataFrame(inflows), "\n")
    print("outputs\n", pan.DataFrame(outflows), "\n")

    chain.diagram()

###                                                                          ###
################################################################################
### INTERLINKED FACTORY TEST####################################################
################################################################################
###                                                                          ###

if test_factory is True:
    print("\nFactory Test\n")

    factory = Factory('excelData/cementFactory.xlsx', 'excelData/cementFactory.xlsx', 'Chain List', 'Connections', name="cement factory")

    print("\nname",factory.name,"\n")
    print("\nchain DF\n",factory.chains_df)
    print("\nconnections DF\n",factory.connections_df)

    factory.build()

    print("\nchain dict:",factory.chain_dict)
    print("\nmain chain:",factory.chain_dict[factory.main_chain])

    inflows, outflows = factory.balance(1.0, var_i='default', write_to_xls=True)

    totals = {'factory inflows': inflows, 'factory outflows': outflows}
    print(pan.DataFrame(totals), "\n")

    factory.balance(1.0, var_i='default')

    factory.diagram()

###                                                                          ###
################################################################################
###  MULTI-FACTORY INDUSTRY TESTS  #############################################
################################################################################
###                                                                          ###

if test_industry is True:
    print("\nIndustry Test\n")

    i_kwargs = dict(factory_list_file='excelData/cementIndustry.xlsx',
                    factory_list_sheet='Factory List', 
                    connections_sheet='Factory Connections', 
                    name='Cement Industry')

    industry = Industry(**i_kwargs)

    industry.build()

    for factory, details in industry.factory_dict.items():
        print(factory, details)

    ioDicts= industry.balance(products_sheet='1990-Absolute', write_to_xls=True, 
                    file_id='1990-Absolute', diagrams=True)


    ioDicts= industry.balance(products_sheet='2010-Relative', write_to_xls=True, 
                    file_id='2010-Relative', diagrams=True)

    ioDicts= industry.balance(products_sheet='2010-Relative', write_to_xls=True, 
                    file_id='2010-Relative-default', force_scenario='default', diagrams=True)

    s_list = ['default', 'EU-typ', 'EU-bat']

    s_kwargs = dict(scenario_list=s_list, 
                    products_sheet='1990-Relative', 
                    write_to_xls=True, 
                    file_id='1990-Relative', 
                    diagrams=False)

    industry.run_scenarios(**s_kwargs)

    e_kwargs = dict(start_sheet='1990-Absolute', 
                    end_sheet='2010-Absolute',
                    start_step=1990,
                    end_step=2010,
                    write_to_xls=True, 
                    diagrams=True)
    industry.evolve(**e_kwargs)
