# IMPORT MODULES
from molmass import Formula
from collections import defaultdict
import pandas as pan
import os
import logging
import sys
import random

# import other BlackBlox modules
from dataconfig import *
from unitprocess import *
from multiprocess import *
from molmass import Formula

#specify number of test runs
runs = 5

# print("\ninititalizing test of refactored blackblox.py\n")

# print("unitlist:")
# print(df_unitList,'\n')

# print("fuel list:")
# print(df_fuels,'\n')

# print("\nTesting calculation classes")

# print("\nRatio Test")
# known = 'A'
# unknown = 'B'

# for i in range(runs):
#     knownQty = random.uniform(0.001,1000)
#     ratio = random.uniform(1,100)
#     unknownQty = knownQty * ratio

#     print("\nusing:\nknown:", known, ", qty:", knownQty, \
#     "\nunknown", unknown, ", qty:", unknownQty, \
#     "\nratio (mass)", ratio,'\n')

#     ratioTest = Ratio(knownQty, ratio)
#     if round(ratioTest,5) == round(unknownQty,5):
#         print("correctly solved for", unknown, ratioTest)
#     else:
#         print("ERROR:", ratioTest, "!=", unknownQty)
#         sys.exit("Something went wrong")

#     ratioTest_i = Ratio(unknownQty, ratio, invert = True)
#     if round(ratioTest_i,5) == round(knownQty,5):
#         print("correctly solved with inversion for:", unknown, ratioTest_i)
#     else:
#         print("ERROR:", ratioTest_i, "!=", knownQty)
#         sys.exit("Something went wrong")

# print("\nRemainder Test")
# known = 'A'
# unknown = 'B'


# for i in range(runs):

#     knownQty = random.uniform(0.001,1000)
#     ratio = random.random()
#     unknownQty = knownQty * (1 - ratio)
#     print("\nusing:\nknown:", known, ", qty:", knownQty, \
#     "\nunknown", unknown, ', qty:', unknownQty, \
#     "\ngiven ratio", ratio, \
#     "\nderived remainder ratio", (1 - ratio), '\n')

#     remainderTest = Remainder(knownQty, ratio)
#     if round(remainderTest,5) == round(unknownQty,5):
#         print("correctly solved for:", unknown, remainderTest)
#     else:
#         print("ERROR:", remainderTest, "!=", unknownQty)
#         sys.exit("Something went wrong")

#     remainderTest_i = Remainder(unknownQty, ratio, invert=True)
#     if round(remainderTest_i,5) == round(knownQty,5):
#         print("correctly solved for:", unknown, remainderTest_i)
#     else:
#         print("ERROR:", remainderTest_i, "!=", knownQty)
#         sys.exit("Something went wrong")

# print("\nMolMassRatio Test")
# molecules = ['H2', 'H2O', 'C2O', 'NH4', 'NH3', 'CaCO3', 'CaO'\
# 'C9H8O4', 'Si', 'NaC18H35O2', 'H2SO4', 'C2H6O', '[2H]2O', '(COOH)2',\
#  'D2O', 'C48H32AgCuO12P2Ru4', 'CH3COOH', 'SO2', 'NaHCO3', 'NaCl', \
#  'NaOH', 'Na2[B4O5(OH)4].5H2O']

# for i in range(runs):
#     known = random.choice(molecules)
#     knownQty = random.uniform(0.001, 1000)
#     unknown = random.choice(molecules)
#     unknownQty = (Formula(unknown).mass / Formula(known).mass) * knownQty

#     print("using:\nknown:", known, ", qty:", knownQty, \
#     "\nunknown", unknown, ", qty:", unknownQty, \
#     "\nratio (mass)", Formula(unknown).mass / Formula(known).mass,'\n')

#     molRatioTest = MolMassRatio(known, knownQty, unknown)
#     if round(molRatioTest,5) == round(unknownQty, 5):
#           print("correctly solved for:", unknown, molRatioTest)
#     else:
#         print("ERROR:", molRatioTest, "!=", round(unknownQty, 5))
#         sys.exit("Something went wrong")      


# print("\nCombustion Test")
# fuels = df_fuels.index.tolist()


# for i in range(runs):
#     known = random.choice(fuels)
#     knownQty = random.uniform(0.001, 1000)
#     unknown = 'heat MJs'
#     combustEff = random.random()
#     unknownQty = knownQty * df_fuels.at[known, 'HHV'] * combustEff
#     emissionsDict = defaultdict(float)

#     print("\nusing:\nknown:", known, ", qty:", knownQty, \
#     "\nunknown;", unknown, ", qty:", unknownQty, \
#     "\nCombustEff;", combustEff,'\n')

#     combustTest1 = Combustion(known, knownQty, unknown, combustEff)
#     if round(combustTest1, 5) == round(unknownQty, 5):
#         print("correctly solved for:", unknown, combustTest1)
#     else:
#         print("ERROR:", combustTest1, "!=", unknownQty)
#         sys.exit("Something went wrong") 

#     combustTest2 = Combustion(unknown, unknownQty, known, combustEff, emissionsDict)
#     if round(combustTest2, 5) == round(knownQty, 5):
#         print("correctly solved for:", unknown, combustTest2)
#         print("and wrote emissions to dictionary:", emissionsDict)
#     else:
#         print("ERROR:", combustTest2, "!=", knownQty)
#         sys.exit("Something went wrong")

# print("\nUnit Process Test")

# units =df_unit_processes.index.tolist()

# for i in range(runs):
#     name = random.choice(units)
#     # product = df_unit_processes.at[name, default_product_col]
#     # i_o = df_unit_processes.at[name, default_product_io_col]
#     qty = random.uniform(0.001, 1000)
#     varDF = makeDF(df_unit_processes.at[name, variables_filepath_col])
#     scenarios = varDF.index.tolist()
#     s = random.choice(scenarios)


#     unit1 = UnitProcess(name)

#     print("\nUsing:", unit1.name, unit1.default_product, qty, unit1.default_io, s)

#     print(unit1.name, "inflows:", unit1.inflows)
#     print(unit1.name, "outflows:", unit1.outflows)

#     u_in, u_out = unit1.balance(qty)
#     print(u_in)
#     print(u_out)

# # Add for random input
#     product = random.choice(tuple(unit1.inflows))
#     # while (product == 'fuel' and len(unit1.inflows) > 1):   #fuel combustion calcs writes CO2 to output in balance; this can mess up numbers if there's something else that writes to CO2. fix this later.
#     #     product = random.choice(tuple(unit1.inflows))
#     qty = u_in[product]

#     if product == 'fuel':
#         qty = u_in[unit1.variables_df.at[s, 'fuelType']]

    
    
#     i_o = "IN"

#     print("\nUsing:",\
#     name, product, i_o, qty, s)
    

#     u1_in, u1_out = unit1.balance(qty, product, i_o, s) 

#     if u1_in == u_in and u1_out == u_out:
#         print("Same input/output as above")
#     else:
#         print("not equivelent to above")
#         print(u1_in)
#         print(u1_out)

# # Add for random output
#     product = random.choice(tuple(unit1.outflows))
    
#     qty = u_out[product]
    
#     if product == 'fuel':
#         qty = u_out[unit1.varDF.at[s, 'fuelType']]
     
#     i_o = "Out!"


#     print("\nUsing:",\
#     name, product, i_o, qty, s)
    
#     u1_in, u1_out = unit1.balance(qty, product, i_o, s) 

#     if u1_in == u_in and u1_out == u_out:
#         print("Same input/output as above")
#     else:
#         print("not equivelent to above")
#         print(u1_in)
#         print(u1_out)

print("\nFlow Test\n")

flowTSV = "chainFiles/cementFlowRefactor.tsv"

cementChain = ProductChain(flowTSV, "cement production")

print(cementChain.name)
print(cementChain.process_chain_df)
print(cementChain.process_list)

cementChain.initialize_chain()
print(cementChain.process_list)

io_dicts = cementChain.balance(1.0, var_i="EU-bat")

print("inputs\n", pan.DataFrame(io_dicts["i"]), "\n")
print("outputs\n", pan.DataFrame(io_dicts["o"]), "\n")

