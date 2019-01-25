#!/usr/local/bin/python3

"""
Author: S.E. Tanzer
Python v 3.7.1
"""

import pandas as pan
from collections import defaultdict as ddict
from molmass import Formula
import os

print("\nWorking directory:", os.getcwd())

# STYLE NOTES TO SELF
# when a DF is a global varialbe call it df_name
# when a DF is a local variable call it nameDF

# print("\nWorking directory:", os.getcwd())

###############################################################################
# IMPORT REFERENCE DATA

#fuels reference dictionary
df_fuels = pan.read_csv("fuels.tsv", sep='\t', skiprows=[1], index_col=0)
# ^ skips unit row. Need to figure out how to automate that later

###############################################################################
# CALCULATOR FUNCTIONS
# these process the calculation requests in the unit process calculation files

def Ratio(qty, ratio):
    return qty * ratio


def MolMassRatio(qty1, sub1, sub2):
    return qty1 * Formula(sub2).mass/Formula(sub1).mass


def Remainder(qty, ratio):
    if ratio > 1:
        print("ratio is greater than one, this calcuation will return a negative number")
        return False
    else:
        return qty * (1-ratio)


def Combustion(energyQty, fuelType, emissionsDict, eff = 1.0, fuelDF = df_fuels):
    #has a variable for efficiency that I can work in later if needed

    fuelQty = energyQty / fuelDF['HHV'][fuelType] * (1/eff)

    emissionsDict['CO2'] += fuelDF['CO2'][fuelType] * fuelQty
    emissionsDict['waste heat'] += energyQty * (1 - eff)

    return fuelQty


###############################################################################
# UNIT PROCESS PROCESSOR

def unitProcess(calcDF, varDF, productName, productQty, productIO, var_i="default"):
# IN:   calcDF: dataFrame with the calculations requested
#       varDF: dataFrame with the variables needed for the calculations
#       var_i: the desired row index of the variable dataFrame (e.g. scenario name)
#       productName: the name of the product that is the final outout of the unit process
#       productQty: the quantity of the final product
#       productIO: str, "Input" or "Output", specifying whether the product is an input or an output
# OUT:  a dictionary of unit process inputs and a dictionary of unit process outputs


    tmpDict = ddict(float) #temporary values dictionary
    inDict = ddict(float)
    outDict = ddict(float)

    #initalizes output dictionary with given product
    if productIO == "output":
        outDict[productName] = productQty
    if productIO == "input":
        inDict[productName] = productQty


    # check that dataFrame is in the right shape
    if list(calcDF) != ['KnownQty', 'k_QtyFrom', 'UnknownQty', 'u_QtyTo', 'Calculation', 'Variable']:
        print("DataFrame does not conform to expected shape")
        return False

    # perform specified calculations in order
    for i in calcDF.index:

        # simplifing variables for more readable code
        k_from = calcDF.at[i, 'k_QtyFrom']
        c_to = calcDF.at[i, 'u_QtyTo']
        calcType = calcDF.at[i, 'Calculation']

        #if no row (scenario) of the variable DF is selected, default to first row
        if var_i not in varDF.index.values:
            var_i = "default"
            if "default" not in varDF.index.values:
                print("scenario not found and no default scenario available.")
                return False

        #Assign dataFrame data to internal variables for more readable code
        if calcDF.at[i, 'k_QtyFrom'] == 'fuel':  #if it's a fuel, specify fuelType for variable DF
            known == varDF.at[var_i, 'fuelType']
        else:
            known = calcDF.at[i, 'KnownQty']

        if calcDF.at[i, 'UnknownQty'] == 'fuel':  #if it's a fuel, specify fuelType for variable DF
            calc = varDF.at[var_i, 'fuelType']
        else:
            calc = calcDF.at[i, "UnknownQty"]

        if calcDF.at[i, 'Variable'] != 'NONE':
            variable = varDF.at[var_i, calcDF.at[i, 'Variable']]
        else:
            variable = False


        # Check that the known substance exits in dictionaries
        if k_from == "output" and outDict[known] > 0:
            qtyKnown = outDict[known]
        elif k_from == "tmp" and tmpDict[known] > 0:
            qtyKnown = tmpDict[known]
        elif k_from == "input" and inDict[known] > 0:
            qtyKnown = inDict[known]
        else:
            print(known, "is 0, negative, or does not exist in dictionaries")
            print("inDict", inDict)
            print("outDict", outDict)
            print("tmpDict", inDict)
            return False

        # performed specified calculation
        if calcType == 'Ratio':
            qtyCalc = Ratio(qtyKnown, variable)

        elif calcType == 'Remainder':
            qtyCalc = Remainder(qtyKnown, variable)

        elif calcType == 'MolMassRatio':
            qtyCalc = MolMassRatio(qtyKnown, known, calc)

        elif calcType  == 'Combustion':
            qtyCalc = Combustion(qtyKnown, calc, outDict, variable)

        else:
            print(calcType, "is unknown calculation type.")
            return False

        # assign calculated quantity to approproriate dictionary key
        if c_to == 'input':
            inDict[calc] += qtyCalc

        elif c_to == 'output':
            outDict[calc] += qtyCalc

        elif c_to == 'tmp':
            tmpDict[calc] += qtyCalc

        else:
            print(c_to, "is unknown destination.")
            return False

        #return dictionaries of inputs and outputs
    return inDict, outDict


###############################################################################
# FUNCTION TO RUN A CHAIN OF MULTIPLE PROCESSES



def checkFlow(flowDF, unitListDF):
# checks to see if the production flow data usable
# production data should be in a linear chain, backwards or forwards
# therefore the first or last line should have a "To" of "END"
# and the other should have a "From" of "START"
# if it is an output based chain, the "START" should be NONE

    last = flowDF.index[-1] # gets index for last row of DF

    #if flow data is output-based and written start->end, reverse it
    if flowDF.at[0,'From'] == 'START' and flowDF.at[0,'What'] == 'NONE':
        flowDF = flowDF[::-1]

    # if output appears output-based, check that everything is actually the
    # correct output product of the correct process
    if flowDF.at[last,'From'] == 'START' and flowDF.at[last,'What'] == 'NONE':
        for i in flowDF.index:
            if i != last:
                if flowDF.at[i, 'What'] != unitListDF.at[flowDF.at[i, 'From'], 'product'] \
                or unitListDF.at[flowDF.at[i, 'From'], 'productType'] != 'output':
                    print(flowDF.at[i, 'What'], "is not an output product of", flowDF.at[i, 'From'])
                    return False
        return flowDF

    #if flow data is input-based and written end->start, reverse it
    if flowDF.at[last, 'From'] == "START" and flowDF.at[last, 'What']  != 'NONE':
        flowDF = flowDF[::-1]

    if flowDF['From'][0] == "START" and flowDF['What'][0] != 'NONE':
        for i in flowDF.index:
            if i != last:
                if flowDF.at[i, 'What'] != unitListDF.at[flowDF.at[i, 'To'], 'product'] \
                or unitListDF.at[flowDF.at[i, 'To'], 'productType'] != 'input':
                    print(flowDF.at[i, 'What'], "is not an input product of", flowDF.at[i, 'From'])
                    return False
        return flowDF

    else:
        print("Something is wrong")
        return False

###############################################################################
# MULTI-UNIT FLOWS

def runChain(flowDF, unitListDF, productQty, var_i="default"):

    # check that chain is valid
    print('checking flow')
    flowDF = checkFlow(flowDF, unitListDF)

    # set direction of flow
    if flowDF.at[0,"To"] == "END" and flowDF.at[0,"From"] != "START":
    #    source = 'To'
        dest = "From"
        IO = "output"

    elif flowDF.at[0,"From"] == "START" and flowDF.at[0,"To"] != "END":
    #    source = "From"
        dest = "To"
        IO = "input"
    else:
        print("Cannot determine chain order")
        return False

    # initialize input and output dictionaries
    # these will contain dictionares of inputs/outputs for each process
    inDict = ddict(lambda: ddict(float))
    outDict = ddict(lambda: ddict(float))

    qty = productQty

    #process chain by individual unit process
    for i in flowDF.index:

        #update process name, product name, and product quantity
        process = flowDF.at[i, dest]
        if process == 'START' or process == 'END':
            break
        product = flowDF.at[i, 'What']

        if dest == "From" and flowDF.at[i,"To"] != "END":
            qty = inDict[prevProcess][product]

        elif dest == "To" and flowDF.at[i,"From"] != "START":
            qty = outDict[prevProcess][product]
            
        varDF= pan.read_csv(unitListDF.at[process, 'varFile'], sep='\t', skiprows=[1], index_col=0)
        calcDF = pan.read_csv(unitListDF.at[process, 'calcFile'], sep='\t')

        print("running unit process", process, "with", IO, qty, product, "for scenario", var_i)
        inDict[process], outDict[process] = unitProcess(calcDF, varDF, product, qty, IO, var_i)

        prevProcess = process

    # creates totals dictionary
    totalIn = ddict(float)
    totalOut = ddict(float)

    for k1, v1 in inDict.items():
         for k2, v2 in v1.items():
             totalIn[k2] += v2

    inDict["Chain"] = totalIn

    for k1, v1 in outDict.items():
         for k2, v2 in v1.items():
             totalOut[k2] += v2

    outDict["Chain"] = totalOut

    #remove intermediate outputs from totals (this should be moved to the system level probably)


    for i in flowDF.index:
        product = flowDF.at[i, "What"]

        if flowDF.at[i, "From"] != 'START' and flowDF.at[i, 'To'] != 'END':
            outDict["Chain"][product] -= outDict[flowDF.at[i, "From"]][product]
            inDict["Chain"][product] -= inDict[flowDF.at[i,"To"]][product]

    return inDict, outDict


###############################################################################
# MULTI-CHAIN SYSTEMS

# first run product chain
# then auxillary chains
# ability to accumulate qty needed from multiple unit processes in the chain
# then figure out how to remove intermediate inputs and outputs

# def RunSystem(systemDF, unitListDF, productQty, var_i="default"):

#     chainDF = pan.read_csv(systemDF.at[process, 'calcFile'], sep='\t')

#     for chain in systemDF:
#          scenarioDict[s]['inputs'], scenarioDict[s]['outputs'] = runChain(chain, unitListDF, productQty, s)

# test: single chain, then input-based aux chains, then mix input/output aux chains, then recycle flows

###############################################################################
# RUN SYSTEMS USING MULTIPLE SCENARIOS (variable sets)

# single chain over multiple scenarios

def RunScenarios(flowDF, unitListDF, scenarioList, productQty):
    
    # Initialize Dictionary
    # scenarioDict[scenario][inDict or OutDict][Process][Substance] = Qty
    scenarioDict = ddict(lambda: ddict(lambda: ddict(float)))

    for s in scenarioList:
        print("\nrunning scenario", s)
        scenarioDict[s]['inputs'], scenarioDict[s]['outputs'] = runChain(flowDF, unitListDF, productQty, s)

    return scenarioDict    

###############################################################################
# OUTPUT RESULTS

# Write data to files

# Generate standard graphs

###############################################################################
# TO DO

# Additional Modules
# * BlackBlox Fade: Run scenarios over time, with changes in variables, and accumulators
# * BlackBlox Gold: add economic assessment

# * BlackBlox Green: LCA 
# * BlackBlox Iridescent: Add Uncertainty


###############################################################################
# RUN TESTS

# test()
