from molmass import Formula
from collections import defaultdict
from IOfunctions import makeDF
from BBconfig import *


# CALCULATION TYPES
class Calculation():
    def __init__(self, known, knownQty, unknown):
        self.known = known
        self.qty = knownQty
        self.unknown = unknown


class Ratio(Calculation):
    calcType = "Ratio Calculation"
    formula = "u = k * ratio(u:k)"

    def __init__(self, known, knownQty, unknown, ratio, invert = False):

        super().__init__(known, knownQty, unknown)
        if invert == True:
            self.ratio = 1/ratio
        else:
            self.ratio = ratio

    def calculate(self):
        return self.qty * self.ratio


class Remainder(Calculation):
    calcType = "Reaminder Calculation"
    formula = "u = k * (1 - ratio(u:k))"
    def __init__(self, known, knownQty, unknown, ratio, invert = False):
        super().__init__(known, knownQty, unknown, invert)
        if invert == True:
            self.ratio = 1 - ratio
        else:
            self.ratio = ratio
   
    def calculate(self):
        if self.ratio > 1:
            print("Error:", self.ratio, "> 1.  This calculation will return a negative number")
            return False
        
        return self.qty * (1 - self.ratio)


class MolMassRatio(Calculation):
    calcType = "Molecular Masss Ratio Calculation"
    formula = "[MolMass](u) / MolMass(k)] * k_qty"
    def __init__(self, known, knownQty, unknown):
        super().__init__(known, knownQty, unknown)

    def calculate(self):    
        return Formula(self.unknown).mass / Formula(self.known).mass * self.qty


class Combustion(Calculation):
    calcType = "Combustion Calculation"
    formula = "Special calculation type:\n \
    for a given mass or energy content of fuel, calculates and return the other \
    and, if provided writes emissions to a given emission dictionary"
    def __init__(self, known, knownQty, unknown, combustEff, emissionDict = False):
        super.__init__(known, knownQty, unknown)
        self.combustEff = combustEff

    def calculate(self):
        if self.known in df_fuels.Index:
            #calculates energy and emissions from given mass quantity of fuel
            self.fuelType = self.known
            self.fuelQty = self.qty
            self.energyQty = self.qty * df_fuels['HHV'][self.fuelType] * self.combustEff
            self.returnQty = self.energyQty

        elif self.unknown in df_fuels.Index:
            #calculates fuel mass and emissions from given quantity of energy
            self.fuelType = self.unknown
            self.energyQty = self.qty
            self.fuelQty = self.energyQty / df_fuels['HHV'][self.fuelType] * (1/self.combustEff)
            self.returnQty = self.fuelQty
        
        else:
            print('Error:', 'neither', self.known, 'nor', self.unknown, 'is a known fuel type')
            return False
        
        
        self.CO2emitted = df_fuels['CO2'][self.fuelType] * self.fuelQty
        self.wasteHeat = self.energyQty * (1 - self.combustEff)

        if emissionDict != False:
            emissionDict['CO2'] += self.CO2emitted
            emissionDict['waste heat'] += self.wasteHeat
        
        else:
            print('\nEmission data discarded: \n \
            CO2:', self.CO2emitted, '\n \
            waste heat:', self.wasteHeat )

        return self.returnQty

# UNIT PROCESS
class UnitProcess:

    def __init__(self, name):
        self.name = name
        self.varDF = makeDF(df_unitList.at[name,ul_varFileLoc])
        self.calcDF = makeDF(df_unitList.at[name,ul_calcFileLoc], index = None)

        #create lists of process inputs and outputs
        self.inputs = []   
        self.outputs = []   
        
        for i in calcDF.index:  
            k = calcDF.at[i, c_known]
            k_from = str.lower(calcDF.at[i, c_kFrom][0]) # takes only first letter of string to ignore typing variance
            u = calcDF.at[i, c_unknown]
            u_to = str.lower(calcDF.at[i, c_uTo][0]) # takes only first letter of string to ignore typing variance
              
            if k_from == 'i':
                self.inputs.append(k)
            elif k_from == 'o':
                self.outputs.append(k)

            if u_to == 'i':
                self.inputs.append(u)
            elif u_to == 'o':
                self.outputs.append(u)
            
 
    def balance(self, product, qty, IO, var_i='default'):
        # product: final input or output on which to balance the calculations
        # qty: desired final quantity of product
        # IO: whether product is an input (i, in, or input) or output (o, out or output)
        # var_i: row index of variables files to use

        inDict = defaultdict(float)
        outDict = defaultdict(float)
        tmpDict = defaultdict(float)

        # Add quantity of desired final product to appropriate dictionary (input or output)
        if str.lower(IO[0]) == 'i':
            inDict[product] = qty
        elif str.lower(IO[0]):
            outDict[product] = qty
        else:
            print('Error:', IO, 'is not a valid input/output identifier')

        if var_i not in varDF.index.values:
            print('Error', var_i, 'not found in variables file')
        
        # perform specified calculations, starting with the known substance
        
        #initalize counters
        i = 0
        attempt = 1
    

        while len(calcDF) > 0:

            # simplify variables
            known = calcDF.at[i, c_known]
            k_from =str.lower(calcDF.at[i, c_kFrom][0]) # shortens to i, o, or t (lower case)
            u_to = str.lower(calcDF.at[i, c_uTo][0]) # shortens to i, o or t (lower case)
            unknown = calcDF.at[i, c_unknown]
            calcType = str.lower(calcDF.at[i, c_calcType])

            # if at end of list, loop around
            if i >= len(calcDF):
                i = 0
            # print("current index:", i, "current product:", known, '\n')

            # prevent infinite loops by terminating afer a complete loop through
            if attempt >= len(calcDF):
                print("Error cannot process", known)
                return False

            # check whether either quantity is a specified lookup variable, and substitute from variable file, if so
            # Check if either quantity is fuel, and substitute fuel type from variable file if so.
            if known in lookupVar:
                known = varDF.at[var_i, lookupVar[known][1]] 
            if unknown in lookupVar:
                unknown = varDF.at[var_i, lookupVar[calc][1]] 

            # Check that the specified "known" quantity exists in input/output dictionaries
            invert = False 
            if k_from == 'o' and outDict[known] > 0:
                qtyKnown = outDict[known]
                #print(known, "confirmed in output dictionary, qty:", qtyKnown)

            elif k_from == "i" and inDict[known] > 0:
                qtyKnown = inDict[known]
                #print(known, "confirmed in input dictionary, qty:", qtyKnown)

            elif k_from == "t" and tmpDict[known] > 0:
                qtyKnown = tmpDict[known]
                #print(known, "confirmed in tmp dictionary, qty:", qtyKnown)  

        # If not, check for the "unknown" quantity, and, if so attempt to invert the calculation
            elif u_to == "o" and outDict[unknown] > 0:
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                invert = True
                qtyKnown = outDict[known]

            elif u_to == "i" and inDict[unknown] > 0:
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                invert = True
                qtyKnown = inDict[known]    

            elif u_to == "t" and tmpDict[unknown] > 0:
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                invert = True
                qtyKnown = tmpDict[known]


            #if invert == True:
                #print(calc, "\nnot found in dictionary; checking for potential inversion...\n", known, "found, qty:", qtyKnown)

            #if substance isn't found start again from the beginning
            else:
                #print("\n neither", known, "nor", calc, "not found, skipping for now\n")
                i += 1
                attempt += 1
                continue

            
            var = varDF.at[var_i, calcDF.at[i, c_var]]


            #print("\nknown qty of", known, "and unknown qty of", calc)


            # performed specified calculation
            if invert == True:
               print("\nattempting calculation with inversion")

            if calcType == 'ratio':
                qtyCalc = Ratio(known, qtyKnown, unknown, var, invert).calculate()
                #print("Ratio calculation performed")

            elif calcType == 'remainder':
                qtyCalc = Remainder(known, qtyKnown, unknown, var, invert).calculate()
                #print("Remainder calculation performed")

            elif calcType == 'molmassratio':
                qtyCalc = MolMassRatio(known, qtyKnown, unknown).calculate()
                #print("MolMass calculation performed")

            elif calcType  == 'combustion':
                # print("performing combustion calcuation on", fuelType, invert)
                qtyCalc = Combustion(known, qtyKnown, unknown, var, outDict).calculate()
                # print("Combustion calculation performed")

            else:
                print(calcType, "is unknown calculation type.")
                return False

            # assign calculated quantity to approproriate dictionary key
            if u_to == 'i':
                inDict[unknown] += qtyCalc
                # print(qtyCalc, unknown, "added to input dictionary")

            elif u_to == 'o':
                outDict[unknown] += qtyCalc
                # print(qtyCalc, unknown, "added to output dictionary")

            elif u_to == 't':
                tmpDict[unknown] += qtyCalc
                # print(qtyCalc, unknown, "added to temp dictionary")

            else:
                # print(u_to, "is unknown destination.")
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