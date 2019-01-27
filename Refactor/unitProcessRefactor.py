# UNIT PROCESS PROCESSOR
# REFACTOR to balance on arbitrary input and output

import pandas as pan
from collections import defaultdict as ddict
from molmass import Formula


###############################################################################
# IMPORT DATA

df_fuels = pan.read_csv("fuels.tsv", sep='\t', skiprows=[1], index_col=0)

###############################################################################
# define test

def test():

    df_var= pan.read_csv('varFiles/ClinkerKilnVar.tsv', sep='\t', skiprows=[1], index_col=0)
    df_calc = pan.read_csv('calcFiles/ClinkerKiln.tsv', sep='\t')

    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    print("Test on Clinker")
    product = "clinker"
    inDict, outDict = unitProcess(df_calc, df_var, product, 1.0, 'output', 'EU-bat')

    print("inputs\n", pan.DataFrame(inDict, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict, index = [0]), "\n")

    print("Test on meal")
    product = "meal"
    qty = 0.928096
    io = 'input'
    inDict2, outDict2 = unitProcess(df_calc, df_var, product, qty, io, 'EU-bat')


    print("Kiln: Test on Clinker")
    print("inputs\n", pan.DataFrame(inDict, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict, index = [0]), "\n")

    print("Kiln: Test on Meal")
    print("inputs\n", pan.DataFrame(inDict2, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict2, index = [0]), "\n")

    df_var= pan.read_csv('varFiles/MealMixerVar.tsv', sep='\t', skiprows=[1], index_col=0)
    df_calc = pan.read_csv('calcFiles/MealMixer.tsv', sep='\t')

    print("Mixer Test on Meal")
    product = "meal"
    inDict, outDict = unitProcess(df_calc, df_var, product, 1.0, 'output', 'EU-bat')

    print("inputs\n", pan.DataFrame(inDict, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict, index = [0]), "\n")

    print("Mixer Test on CaCo3")
    product = "CaCO3"
    qty = 0.65
    io = 'input'
    inDict2, outDict2 = unitProcess(df_calc, df_var, product, qty, io, 'EU-bat')

    print("Mixer Test on Clay")
    product = "clay"
    qty = 0.25
    io = 'input'
    inDict3, outDict3 = unitProcess(df_calc, df_var, product, qty, io, 'EU-bat')


    print("Mixer: Test on Meal")
    print("inputs\n", pan.DataFrame(inDict, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict, index = [0]), "\n")

    print("Kiln: Test on CaCO3")
    print("inputs\n", pan.DataFrame(inDict2, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict2, index = [0]), "\n")

    print("Kiln: Test on Clay")
    print("inputs\n", pan.DataFrame(inDict3, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict3, index = [0]), "\n")


def unitProcess(calcDF, varDF, productName, productQty, productIO, var_i="default"):
# IN:   calcDF: dataFrame with the calculations requested
#       varDF: dataFrame with the variables needed for the calculations
#       var_i: the desired row index of the variable dataFrame (e.g. scenario name)
#       productName: the name of the product that is the final outout of the unit process
#       productQty: the quantity of the final product
#       productIO: str, "input" or "iutput", specifying whether the product is an input or an output
# OUT:  a dictionary of unit process inputs and a dictionary of unit process outputs


    tmpDict = ddict(float) #temporary values dictionary
    inDict = ddict(float)
    outDict = ddict(float)

    # check that dataFrame is in the right shape
    for col in ['KnownQty', 'k_QtyFrom', 'UnknownQty', 'u_QtyTo', 'Calculation', 'Variable']:
        if col not in list(calcDF):
            print(col, "column is missing from the dataFrame")
            return False

    #initalizes output dictionary with given product
    if productName == 'fuel':
        productName = varDF.at[var_i, 'fuelType']

    if productIO.lower() in ['o', 'out', 'output']:
        outDict[productName] = productQty
        IO = "output"
        print(productQty, productName, 'added to outputDict:\n', outDict)
    elif productIO.lower() in ['i', 'in', 'input']:
        inDict[productName] = productQty
        IO = "input"
        print(productQty, productName, 'added to inputDict\n', inDict)

    else:
        print(productIO, 'is not a valid input/output identifier.')


    # perform specified calculations, starting with the known substance
    i = 0
    attempt = 1

    while len(calcDF) > 0:
        if i >= len(calcDF):
            i = 0
        #simplify variables
        known = calcDF.at[i, 'KnownQty']
        k_from = calcDF.at[i, 'k_QtyFrom']
        c_to = calcDF.at[i, 'u_QtyTo']
        calc = calcDF.at[i, "UnknownQty"]
        calcType = calcDF.at[i, 'Calculation']

        print("current index:", i, "current product:", known, '\n')

        if attempt >= len(calcDF):
            print("Error cannot process", known)
            return False

        #Check if quantities are fuel and whether variables are given.
        if known == 'fuel':  #if it's a fuel, specify fuelType for variable DF
            known = varDF.at[var_i, 'fuelType']

        if calc == 'fuel':  #if it's a fuel, specify fuelType for variable DF
            calc = varDF.at[var_i, 'fuelType']  

        # Check that the known substance exits in dictionaries
        invert = False 
        if k_from == "output" and outDict[known] > 0:
            qtyKnown = outDict[known]
            print(known, "confirmed in output dictionary, qty:", qtyKnown)

        elif k_from == "input" and inDict[known] > 0:
            qtyKnown = inDict[known]
            print(known, "confirmed in input dictionary, qty:", qtyKnown)

        elif k_from == "tmp" and tmpDict[known] > 0:
            qtyKnown = tmpDict[known]
            print(known, "confirmed in tmp dictionary, qty:", qtyKnown)  

        # Check that the "unknown" substance exits in dictionaries
        # and if so, attempt inverting the calculation
        elif c_to == "output" and outDict[calc] > 0:
            known, calc = calc, known
            k_from, c_to = c_to, k_from
            invert = True
            qtyKnown = outDict[known]
            print(calc, "\nnot found in dictionary; checking for potential inversion...\n", known, "confirmed in output dictionary, qty:", qtyKnown)

        elif c_to == "input" and inDict[calc] > 0:
            known, calc = calc, known
            k_from, c_to = c_to, k_from
            invert = True
            qtyKnown = inDict[known]
            print(calc, "\nnot found in dictionary; checking for potential inversion...\n", known, "confirmed in input dictionary, qty:", qtyKnown)
   
        elif c_to == "tmp" and tmpDict[calc] > 0:
            known, calc = calc, known
            k_from, c_to = c_to, k_from
            invert = True
            qtyKnown = tmpDict[known]
            print(calc, "\nnot found in dictionary; checking for potential inversion...\n", known, "confirmed in tmp dictionary, qty:", qtyKnown)

        #if substance isn't found start again from the beginning
        else:
            print("\n neither", known, "nor", calc, "not found, skipping for now\n")
            i += 1
            attempt += 1
            continue

        #Check if quantities are fuel and whether variables are given.
        if known == 'fuel':  #if it's a fuel, specify fuelType for variable DF
            known = varDF.at[var_i, 'fuelType']

        if calc == 'fuel':  #if it's a fuel, specify fuelType for variable DF
            calc = varDF.at[var_i, 'fuelType']  
        
        #if no row (scenario) of the variable DF is selected, default to first row
        if var_i not in varDF.index.values:
            var_i = "default"
            if "default" not in varDF.index.values:
                print("scenario not found and no default scenario available.")
                return False
        

        if calcDF.at[i, 'Variable'] != 'NONE':
            variable = varDF.at[var_i, calcDF.at[i, 'Variable']]
        else:
            variable = False

        print("\nknown qty of", known, "and unknown qty of", calc)

        # performed specified calculation
        if invert == True:
            print("\nattempting calculation inversion")

        if calcType == 'Ratio':
            qtyCalc = Ratio(qtyKnown, variable, invert)
            print("Ratio calculation performed")

        elif calcType == 'Remainder':
            qtyCalc = Remainder(qtyKnown, variable, invert)
            print("Remainder calculation performed")

        elif calcType == 'MolMassRatio':
            qtyCalc = MolMassRatio(qtyKnown, known, calc)
            print("MolMass calculation performed")

        elif calcType  == 'Combustion':
            if invert == True:
                print("performing combustion calcuation on", known, invert)
                qtyCalc = Combustion(qtyKnown, known, outDict, variable, invert=True)
            else: 
                print("performing combustion calcuation on", calc, invert)
                qtyCalc = Combustion(qtyKnown, calc, outDict, variable)
            print("Combustion calculation performed")

        else:
            print(calcType, "is unknown calculation type.")
            return False

        # assign calculated quantity to approproriate dictionary key
        if c_to == 'input':
            inDict[calc] += qtyCalc
            print(qtyCalc, calc, "added to", c_to, "dictionary")

        elif c_to == 'output':
            outDict[calc] += qtyCalc
            print(qtyCalc, calc, "added to", c_to, "dictionary")

        elif c_to == 'tmp':
            tmpDict[calc] += qtyCalc
            print(qtyCalc, calc, "added to", c_to, "dictionary")

        else:
            print(c_to, "is unknown destination.")
            return False
        
        calcDF = calcDF.drop(i)
        calcDF = calcDF.reset_index(drop=True)

        print(len(calcDF), "calculations remaining.")
        attempt = 0

        #return dictionaries of inputs and outputs

    print("inputs\n", pan.DataFrame(inDict, index = [0]), "\n")
    print("outputs\n", pan.DataFrame(outDict, index = [0]), "\n")
    print("temp\n", pan.DataFrame(tmpDict, index = [0]), "\n")
    return inDict, outDict



###############################################################################
# CALCULATOR FUNCTIONS
# these process the calculation requests in the unit process calculation files

def Ratio(qty, ratio, invert=False):
    if invert == True:
        return qty * (1/ratio)
    else:
        return qty * ratio


def MolMassRatio(qty, sub1, sub2):
    return qty * Formula(sub2).mass/Formula(sub1).mass


def Remainder(qty, ratio, invert=False):
    if ratio > 1:
        print("ratio is greater than one, this calcuation will return a negative number")
        return False
    elif invert == True:
        return qty * (ratio)
    else:
        return qty * (1-ratio)


def Combustion(qty, fuelType, emissionsDict, eff = 1.0, fuelDF = df_fuels, invert = False):
    #has a variable for efficiency that I can work in later if needed
    # qty assumes qty of fuel in MJ, returns kg of fuel
    # if inverted, qty assumes qty of fuel in kg, returns mj of energy

    if invert == True:
        print(invert, fuelType, qty, fuelDF['HHV'][fuelType], eff)
        energyQty = qty * fuelDF['HHV'][fuelType] * eff
        emissionsDict['CO2-fuel'] += fuelDF['CO2'][fuelType] * qty
        emissionsDict['waste heat'] += energyQty * (1 - eff)
        print("added CO2", fuelDF['CO2'][fuelType] * qty)

        return energyQty
    
    else:
        fuelQty = qty / fuelDF['HHV'][fuelType] * (1/eff)

        emissionsDict['CO2'] += fuelDF['CO2'][fuelType] * fuelQty
        emissionsDict['waste heat'] += qty * (1 - eff)

        return fuelQty

###############################################################################
test()