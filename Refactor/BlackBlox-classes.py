from molmass import Formula


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
        if self.invert == True:
            self.ratio = 1/ratio
        else:
            self.ratio = ratio

    def calculate(self):
        return self.qty * self.ratio

class Remainder(Calculation):
    calcType = "Reaminder Calculation"
    formula = "u = k * (1 - ratio(u:k))
    def __init__(self, known, knownQty, unknown, ratio, invert = False):
        super().__init__(known, knownQty, unknown, invert)
        if self.invert == True:
            self.ratio = 1 - ratio
        else self.ratio = ratio
   
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
    and, if provided writes emissions to a given emission dictionary
    def __init__(self, known, knownQty, unknown, combustEff, emissionDict = False)
        super.__init__(known, knownQty, sunknown)
        self.combustEff = combustEff

    def calculate(self):
        if self.known in fuelDF.Index:
            #calculates energy and emissions from given mass quantity of fuel
            self.fuelType = self.known
            self.fuelQty = self.qty
            self.energyQty = self.qty * fuelDF['HHV'][self.fuelType] * self.combustEff
            self.returnQty = self.energyQty

        elif unknown in fuelDF.Index:
            #calculates fuel mass and emissions from given quantity of energy
            self.fuelType = self.unknown
            self.energyQty = self.qty
            self.fuelQty = self.energyQty / fuelDF['HHV'][self.fuelType] * (1/self.combustEff)
            self.returnQty = self.fuelQty
        
        else:
            print('Error:', 'neither', self.known, 'nor', self.unknown, 'is a known fuel type')
            return False
        
        
        self.CO2emitted = fuelDF['CO2'][self.fuelType] * self.fuelQty
        self.wasteHeat = self.energyQty * (1 - self.combustEff)

        if emissionDict != False:
            emissionDict['CO2'] += self.CO2emitted
            emissionDict['waste heat'] += self.wasteHeat
            else:
                print('\nEmission data not stored: \n \
                CO2:', self.CO2emitted, '\n \
                waste heat:', self.wasteHeat )

        return self.returnQty


class UnitProcess:

    def __init__(self, name):
        self.name = name
        self.varDF = makeDF(df_unitList.at[name,varFile])
        self.calcDF = makeDF(df_unitList.at[name,calcFile], index = None)
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

            # Add quantity of desired final product to appropriate dictionary (input or output)
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

                # HARD CODED SPECIAL CASE: FUEL TYPE 
                # Check if either quantity is fuel, and substitute fuel type from variable file if so.
                    if known == 'fuel':
                        known = varDF.at[var_i, 'fuelType'] 
                    if calc == 'fuel'
                        calc = varDF.at[var_i, 'fuelType'] 

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
                    elif c_to == "input" and inDict[calc] > 0:
                        known, calc = calc, known
                        k_from, c_to = c_to, k_from
                        invert = True
                        qtyKnown = inDict[known]            
                    elif c_to == "tmp" and tmpDict[calc] > 0:
                        known, calc = calc, known
                        k_from, c_to = c_to, k_from
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