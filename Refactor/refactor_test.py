# IMPORT MODULES
from molmass import Formula
from collections import defaultdict
import pandas as pan
import os
import logging
import sys

# import other BlackBlox modules
from BBconfig import *
from BlackBloxClasses import *

print("\ninititalizing test of refactored blackblox.py\n")

print("\nimporting unitlist:")
print(df_unitList,'\n')

print("\nimporting fuel list:")
print(df_fuels,'\n')

print("\nTesting calculation classes")

print("\nRatio Test")
ratioCalc = Ratio('k', 3, 'u', 2.0)
print(ratioCalc.unknown, ratioCalc.calculate())

ratioCalcInvert = Ratio('u', 6, 'k', 2.0, invert = True)
print(ratioCalcInvert.unknown, ratioCalcInvert.calculate())

print("\nRemainder Test")
print("to be added\n")

print("\nMolMassRatio Test")

print("to be added\n")

print("\nCombustion Test")
print("to be added\n")

print("\nUnit Process Test")
print("to be added\n")