from molmass import Formula


# Classes for the Calculations might not make sense, actually
# It just seems to add lots of extra complication where it's not needed.
# class RatioCalc():
#     def __init__(self, knownQty, variable, invert = False)

#     def calculate():
#         if invert == True:
#             var = 1/var
#         return qty * var

# class RemainderCalc():
#     def calculate():
#         if ratio > 1:
#             print("Error:", ratio, "> 1.  This calculation will return a negative number")
#         else:
#             if invert == False:
#                 var = 1 - var
#             return qty * var

# class MolMassRatioCalc():
#     def __init__(self, knownQty, fuelType, CombustEff, invert = False)

#     return Formula(unknown).mass / Formula (known).mass * qty


# class CombustionCalc():
#     def __init__(self, knownQty, fuelType, CombustEff, invert = False)

#     def Calculate(knownQty, CombustEff):
#         if invert == False:
#             #calculates energy and emissions from given mass quantity of fuel
#             energyQty = qty * fuelDF['HHV'][fuelType] * CombustEff
            
#             outDict['CO2'] += fuelDF['CO2'][fuelType] * qty
#             outDict['waste heat'] += energyQty * (1 - CombustEff)
            
#             return energyQty

#         if invert == True:
#             #calculates fuel mass and emissions from given quantity of energy
#             fuelQty = qty / fuelDF['HHV'][known] * (1/CombustEff)

#             outDict['CO2'] += fuelDF['CO2'][known] * fuelQty
#             outDict['waste heat'] += qty * (1 - CombustEff)

#             return fuelQty


class UnitProcess:

    def __init__(self, name):
        self.name = name
        self.varDF = makeDF(varDir+df_unitList.at[name,varFile], index = varIndex)
        self.calcDF = makeDF(calcDir+df_unitList.at[name,calcFile], index = calcIndex)
        self.product = product
        self.qty = productQty
        self.IO = str.lower(productIO[0])

        self.inputs = []
        self.outputs = []
        
        # initialize input/output dictionary with empty keys
        for i in calcDF.index:
            k = calcDF.at[i, 'KnownQty']
            k_from = str.lower(calcDF.at[i, 'k_QtyFrom'][0])
            u = calcDF.at[i, "UnknownQty"]
            u_to = str.lower(calcDF.at[i, 'u_QtyTo'][0])
              
            if k_from = 'i':
                self.inputs.append(k)
            elif k_from = 'o':
                self.outputs.append(k)

            if u_to = 'i':
                self.inputs.append(u)
            elif u_to = 'o':
                self.outputs.append(u)
            
 
        def balance(self, product, qty, IO, var_i='default'):
            # product: final input or output on which to balance the calculations
            # qty: desired final quantity of product
            # IO: whether product is an input (i, in, or input) or output (o, out or output)
            # var_i: row index of variables files to use

            inDict = defaultdict(float)
            outDict = defaultdict(float)
            tmpDict = defaultdict(float)

            # verify parameters
            if str.lower(IO[0]) == 'i':
            inDict[product] = qty
            elif str.lower(IO[0]):
            outDict[product] = qty
            else:
            print('Error:', IO, 'is not a valid input/output identifier')

            if var_i not in varDF.index.values:
                print('Error', var_i, 'not found in variables file)
            
            # perform specified calculations, starting with the known substance
            
            #initalize counters
            i = 0
            attempt = 1
        

            while len(calcDF) > 0:

                # simplify variables
                known = calcDF.at[i, 'KnownQty']
                k_from = calcDF.at[i, 'k_QtyFrom']
                c_to = calcDF.at[i, 'u_QtyTo']
                calc = calcDF.at[i, "UnknownQty"]
                calcType = calcDF.at[i, 'Calculation']

                # if at end of list, loop around
                if i >= len(calcDF):
                i = 0
                # print("current index:", i, "current product:", known, '\n')

                # prevent infinite loops by terminating afer a complete loop through
                if attempt >= len(calcDF):
                    print("Error cannot process", known)
                    return False

                #Check if either quantity is fuel, and substitute fuel type from variable file if so.
                    if known == 'fuel': 
                        known = varDF.at[var_i, 'fuelType']
                        fuelType = varDF.at[var_i, 'fuelType']

                    if calc == 'fuel': 
                        calc = varDF.at[var_i, 'fuelType']
                        fuelType = varDF.at[var_i, 'fuelType']  

                # Check that the specified "known" quantity exists in input/output dictionaries
                    invert = False 
                    if k_from == "output" and outDict[known] > 0:
                    qtyKnown = outDict[known]
                    #print(known, "confirmed in output dictionary, qty:", qtyKnown)

                    elif k_from == "input" and inDict[known] > 0:
                        qtyKnown = inDict[known]
                        #print(known, "confirmed in input dictionary, qty:", qtyKnown)

                    elif k_from == "tmp" and tmpDict[known] > 0:
                        qtyKnown = tmpDict[known]
                        #print(known, "confirmed in tmp dictionary, qty:", qtyKnown)  

                # If not, check for the "unknown" quantity, and, if so attempt to invert the calculation
                    elif c_to == "output" and outDict[calc] > 0:
                        known, calc = calc, known
                        k_from, c_to = c_to, k_from
                        invert = True
                        qtyKnown = outDict[known]
                        #print(calc, "\nnot found in dictionary; checking for potential inversion...\n", known, "confirmed in output dictionary, qty:", qtyKnown)

                    elif c_to == "input" and inDict[calc] > 0:
                        known, calc = calc, known
                        k_from, c_to = c_to, k_from
                        invert = True
                        qtyKnown = inDict[known]
                        #print(calc, "\nnot found in dictionary; checking for potential inversion...\n", known, "confirmed in input dictionary, qty:", qtyKnown)
            
                    elif c_to == "tmp" and tmpDict[calc] > 0:
                        known, calc = calc, known
                        k_from, c_to = c_to, k_from
                        invert = True
                        qtyKnown = tmpDict[known]
                        #print(calc, "\nnot found in dictionary; checking for potential inversion...\n", known, "confirmed in tmp dictionary, qty:", qtyKnown)

                    #if substance isn't found start again from the beginning
                    else:
                        #print("\n neither", known, "nor", calc, "not found, skipping for now\n")
                        i += 1
                        attempt += 1
                        continue

                    
                    variable = varDF.at[var_i, calcDF.at[i, 'Variable']]


                    #print("\nknown qty of", known, "and unknown qty of", calc)

                    if calcType == 'Ratio':

                    # performed specified calculation
                    #if invert == True:
                    #    print("\nattempting calculation inversion")

                    if calcType == 'Ratio':
                        qtyCalc = Ratio(qtyKnown, variable, invert)
                        #print("Ratio calculation performed")

                    elif calcType == 'Remainder':
                        qtyCalc = Remainder(qtyKnown, variable, invert)
                        #print("Remainder calculation performed")

                    elif calcType == 'MolMassRatio':
                        qtyCalc = MolMassRatio(qtyKnown, known, calc)
                        #print("MolMass calculation performed")

                    elif calcType  == 'Combustion':
                        # print("performing combustion calcuation on", fuelType, invert)
                        qtyCalc = Combustion(qtyKnown, fuelType, outDict, variable, invert)
                        # print("Combustion calculation performed")

                    else:
                        print(calcType, "is unknown calculation type.")
                        return False

                    # assign calculated quantity to approproriate dictionary key
                    if c_to == 'input':
                        inDict[calc] += qtyCalc
                        # print(qtyCalc, calc, "added to", c_to, "dictionary")

                    elif c_to == 'output':
                        outDict[calc] += qtyCalc
                        # print(qtyCalc, calc, "added to", c_to, "dictionary")

                    elif c_to == 'tmp':
                        tmpDict[calc] += qtyCalc
                        # print(qtyCalc, calc, "added to", c_to, "dictionary")

                    else:
                        # print(c_to, "is unknown destination.")
                        return False
                    
                    calcDF = calcDF.drop(i)
                    calcDF = calcDF.reset_index(drop=True)

                    # print(len(calcDF), "calculations remaining.")
                    attempt = 0

                    #return dictionaries of inputs and outputs

                # print("inputs\n", pan.DataFrame(inDict, index = [0]), "\n")
                # print("outputs\n", pan.DataFrame(outDict, index = [0]), "\n")
                # print("temp\n", pan.DataFrame(tmpDict, index = [0]), "\n")
                return inDict, outDict