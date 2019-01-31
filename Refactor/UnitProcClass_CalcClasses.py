from molmass import Formula
from collections import defaultdict
from IOfunctions import makeDF
from BBconfig import *
from Calculators_Classes import *



# UNIT PROCESS
class UnitProcess:

    def __init__(self, name):
        self.name = name
        self.varDF = makeDF(df_unitList.at[name,ul_varFileLoc])
        self.calcDF = makeDF(df_unitList.at[name,ul_calcFileLoc], index=None)

        #create lists of process inputs and outputs
        self.inputs = []   
        self.outputs = []   
        
        for i in self.calcDF.index:  
            k = self.calcDF.at[i, c_known]
            k_from = str.lower(self.calcDF.at[i, c_kFrom][0]) # takes only first letter of string to ignore typing variance
            u = self.calcDF.at[i, c_unknown]
            u_to = str.lower(self.calcDF.at[i, c_uTo][0]) # takes only first letter of string to ignore typing variance
              
            if k_from == 'i':
                self.inputs.append(k)
            elif k_from == 'o':
                self.outputs.append(k)

            if u_to == 'i':
                self.inputs.append(u)
            elif u_to == 'o':
                self.outputs.append(u)
            
 
    def balance(self, product, qty, i_o, var_i='default'):
        # product: final input or output on which to balance the calculations
        # qty: desired final quantity of product
        # i_o: whether product is an input (i, in, or input) or output (o, out or output)
        # var_i: row index of variables files to use
        calcDF = self.calcDF
        inDict = defaultdict(float)
        outDict = defaultdict(float)
        tmpDict = defaultdict(float)

        #verify input
        if product not in self.inputs and product not in self.outputs:
            raise Exception('{} not found in {} input or output sets'.format(product, self.name))

        if var_i not in self.varDF.index.values:
            raise Exception('{} not found in variables file'.format(var_i))

        if str.lower(i_o[0] not in ['i', 'o', 't']:
            raise Exception('{} not valid product destination'.format(i_o))
    
        
        # perform specified calculations, starting with the known substance
        
        #initalize counters
        i = 0
        attempt = 0
    

        while len(calcDF) > 0:
                       
            if i >= len(calcDF):     # if at end of list, loop around
                i = 0

            # simplify variables
            known = calcDF.at[i, c_known]
            k_from =str.lower(calcDF.at[i, c_kFrom][0]) # shortens to i, o, or t (lower case)
            u_to = str.lower(calcDF.at[i, c_uTo][0]) # shortens to i, o or t (lower case)
            unknown = calcDF.at[i, c_unknown]
            calcType = str.lower(calcDF.at[i, c_calcType])

           # print("current index:", i, "current product:", known, '\n')

            if attempt >= len(calcDF):  # prevent infinite loops by terminating afer a complete loop through
                print("Error cannot process", known)
                return False

            # check whether either quantity is a specified lookup variable, and substitute from variable file, if so
            if known in lookupVar:
                known = self.varDF.at[var_i, lookupVar[known][1]] 
            if unknown in lookupVar:
                unknown = self.varDF.at[var_i, lookupVar[unknown][1]] 

            # Check that the specified "known" quantity exists in input/output dictionaries
            invert = False 
            if k_from == 'o' and known in outDict:
                qtyKnown = outDict[known]
                #print(known, "confirmed in output dictionary, qty:", qtyKnown)

            elif k_from == "i" and known in inDict:
                qtyKnown = inDict[known]
                #print(known, "confirmed in input dictionary, qty:", qtyKnown)

            elif k_from == "t" and known in tmpDict:
                qtyKnown = tmpDict[known]
                #print(known, "confirmed in tmp dictionary, qty:", qtyKnown)  

            # If not, check for the "unknown" quantity, and, if so attempt to invert the calculation
            elif u_to == "o" and unknown in outDict:
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                invert = True
                qtyKnown = outDict[known]

            elif u_to == "i" and unknown in inDict:
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                invert = True
                qtyKnown = inDict[known]    

            elif u_to == "t" and unknown in tmpDict:
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                invert = True
                qtyKnown = tmpDict[known]

            
            else:   #if substance isn't found start again from the beginning
               # print("\n neither", known, "nor", unknown, "not found, skipping for now\n")
                i += 1
                attempt += 1
                continue

            # verify variable
            if calcDF.at[i, c_var] not in ignoreVar:  
                var = self.varDF.at[var_i, calcDF.at[i, c_var]] 
            else: var = False
            #print("\nknown qty of", known, "and unknown qty of", unknown)


            # performed specified calculation
            # if invert == True:
                # print("\nattempting calculation with inversion")

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
                print(u_to, "is unknown destination.")
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