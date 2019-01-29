# IMPORT MODULES
from molmass import Formula
from collections import defaultdict
import pandas as pan
import os
import logging
import sys
import random

# import other BlackBlox modules
from BBconfig import *
from BlackBloxClasses import *
from molmass import Formula

#specify number of test runs
runs = 10

print("\ninititalizing test of refactored blackblox.py\n")

print("unitlist:")
print(df_unitList,'\n')

print("fuel list:")
print(df_fuels,'\n')

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

#     ratioTest = Ratio(known, knownQty, unknown, ratio)
#     if round(ratioTest.calculate(),5) == round(unknownQty,5):
#         print("correctly solved for", ratioTest.unknown, ratioTest.calculate())
#     else:
#         print("ERROR:", ratioTest.calculate(), "!=", unknownQty)
#         sys.exit("Something went wrong")

#     ratioTest_i = Ratio(unknown, unknownQty, known, ratio, invert = True)
#     if round(ratioTest_i.calculate(),5) == round(knownQty,5):
#         print("correctly solved with inversion for:", ratioTest_i.unknown, ratioTest_i.calculate())
#     else:
#         print("ERROR:", ratioTest_i.calculate(), "!=", knownQty)
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

#     remainderTest = Remainder(known, knownQty, unknown, ratio)
#     if round(remainderTest.calculate(),5) == round(unknownQty,5):
#         print("correctly solved for:", remainderTest.unknown, remainderTest.calculate())
#     else:
#         print("ERROR:", remainderTest.calculate(), "!=", unknownQty)
#         sys.exit("Something went wrong")

#     remainderTest_i = Remainder(unknown, unknownQty, known, ratio, invert=True)
#     if round(remainderTest_i.calculate(),5) == round(knownQty,5):
#         print("correctly solved for:", remainderTest_i.unknown, remainderTest_i.calculate())
#     else:
#         print("ERROR:", remainderTest_i.calculate(), "!=", knownQty)
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
#     if round(molRatioTest.calculate(),5) == round(unknownQty, 5):
#           print("correctly solved for:", molRatioTest.unknown, molRatioTest.calculate())
#     else:
#         print("ERROR:", molRatioTest.calculate(), "!=", round(unknownQty, 5))
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
#     if round(combustTest1.calculate(), 5) == round(unknownQty, 5):
#         print("correctly solved for:", combustTest1.unknown, combustTest1.calculate())
#     else:
#         print("ERROR:", combustTest1.calculate(), "!=", unknownQty)
#         sys.exit("Something went wrong") 

#     combustTest2 = Combustion(unknown, unknownQty, known, combustEff, emissionsDict)
#     if round(combustTest2.calculate(), 5) == round(knownQty, 5):
#         print("correctly solved for:", combustTest2.unknown, combustTest2.calculate())
#         print("and wrote emissions to dictionary:", emissionsDict)
#     else:
#         print("ERROR:", combustTest2.calculate(), "!=", knownQty)
#         sys.exit("Something went wrong")

print("\nUnit Process Test")

units = df_unitList.index.tolist()

for i in range(runs):
    name = random.choice(units)
    product = df_unitList.at[name, ul_product]
    i_o = df_unitList.at[name, ul_productIO]
    qty = random.uniform(0.001, 1000)
    varDF = makeDF(df_unitList.at[name,ul_varFileLoc])
    scenarios = varDF.index.tolist()
    s = random.choice(scenarios)

    print("\nUsing:",\
    name, product, i_o, qty, s)

    unit1 = UnitProcess(name)
    print(unit1.name, "inputs:", unit1.inputs)
    print(unit1.name, "outputs:", unit1.outputs)

    u1_in, u1_out = unit1.balance(product, qty, i_o, s)
    print(u1_in)
    print(u1_out)

# Add for random non-fuel input and output
    # product = random.choice(u1.inputs)
    # i_o = "IN"
    # qty = random.uniform(0.001, 1000)


