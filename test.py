#!/usr/local/bin/python3

"""
Author: S.E. Tanzer
Python v 3.7.1
"""

import BlackBlox as bb
import pandas as pan
from collections import defaultdict as ddict


###############################################################################
# IMPORT DATA


# flows with 
df_unitList = pan.read_csv('unitList.tsv', sep='\t', index_col = 0)
df_flowIO = pan.read_csv('CO2CapFlow.tsv', sep='\t', index_col=None)
df_flowOI = pan.read_csv('cementProdFlow.tsv', sep='\t', index_col=None)

print("\n")

#---------------------------------------------
print("CALCULATOR FUNCTION TESTS\n")

print("Ratio")
print(5, 0.5,"\n", bb.Ratio(5,0.5),"\n")

print("MolMassRatio")
print(5, "C", "CO2","\n", bb.MolMassRatio(5, "C", "CO2"),"\n")

print("Remainder")
print(5, 0.5,"\n", bb.Remainder(5,0.5),"\n")

print("Combustion")
emDict = ddict(float)
print(33.7, "coal", "emDict", "eff = 1.0", "\n", bb.Combustion(33.7,"coal", emDict),"\n")
print(emDict)

#---------------------------------------------
print("UNIT PROCESS FUNCTION TEST")

df_var= pan.read_csv('varFiles/ClinkerKilnVar.tsv', sep='\t', skiprows=[1], index_col=0)
df_calc = pan.read_csv('calcFiles/ClinkerKiln.tsv', sep='\t')

product = "clinker"

print(df_calc, df_var, product, 1.0, 'output', 'EU-bat')
inDict, outDict = bb.unitProcess(df_calc, df_var, product, 1.0, 'output', 'EU-bat')

print("inputs\n", pan.DataFrame(inDict, index = [0]), "\n")
print("outputs\n", pan.DataFrame(outDict, index = [0]), "\n")

#---------------------------------------------
print("FLOWCHECK TESTS\n")


print("forward flow\n", bb.checkFlow(df_flowIO, df_unitList),"\n")
print("backward flow\n", bb.checkFlow(df_flowOI, df_unitList),"\n")

#---------------------------------------------
print("MULTI UNIT FLOW TESTS\n")

print("Input-based chain: CO2 cap\n")
inDict, outDict = bb.runChain(df_flowIO, df_unitList, 1.0, 'EU-bat')

print("inputs\n", pan.DataFrame(inDict), "\n")
print("outputs\n", pan.DataFrame(outDict), "\n")

print("input-based chain: Cement Prod\n")
inDict, outDict = bb.runChain(df_flowOI, df_unitList, 10, 'default')

print("inputs\n", pan.DataFrame(inDict), "\n")
print("outputs\n", pan.DataFrame(outDict), "\n")

print("MULTI SCENARIO TESTS\n")

s = ['EU-bat', 'EU-typ', 'EU-old']
scenarioDict = bb.RunScenarios(df_flowOI, df_unitList, s, 1.0)

for s in scenarioDict.keys():
    print("scenario:", s)
    print("inputs\n", pan.DataFrame(scenarioDict[s]['inputs']), "\n")
    print("outputs\n", pan.DataFrame(scenarioDict[s]['outputs']), "\n")
