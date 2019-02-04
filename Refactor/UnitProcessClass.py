from molmass import Formula
from collections import defaultdict
from IOfunctions import makeDF
from BBconfig import *
from Calculators import *
import logging

logging.basicConfig(filename='refactor.log',level=logging.DEBUG)


# UNIT PROCESS
class UnitProcess:
    """
    UnitProcess objects have a set of inputs and outputs, with the relationship 
    between them expressed in a DataFrame of calculations and a DataFrame of 
    variables to use in the calculations.

    The sets of inputs and outputs is derived from the list of calculation 
    supplied by the user.

    UnitProcess.balance allows the user to specify a specific quantity of an 
    input and , and a specific set of calculation variables to use, and the 
    function will return dictionaries (defaultdict) of the quantities of the 
    unit process inputs and outputs to balance the given product quantity.
    """

    def __init__(self, name, varDF = False, calcDF = FalseunitListDF = False):
        self.name = name

        if isinstance(varDF, pan.DataFrame):
            self.varDF = varDF
        else:
            self.varDF = makeDF(df_unitList.at[name,ul_varFileLoc])

        if isinstance(calc, pan.DataFrame):
            self.calcDF = calcDF
        self.calcDF = makeDF(df_unitList.at[name,ul_calcFileLoc], index=None)

        #create sets of process inputs and outputs
        self.inputs = set() 
        self.outputs = set() 

        
        for i in self.calcDF.index: 

            # list of tuples of the known/unknown products
            # and whether they are process inputs or outputs  
            products = [ (self.calcDF.at[i, c_known], str.lower(self.calcDF.at[i, c_kFrom])),\
                 (self.calcDF.at[i, c_unknown],str.lower(self.calcDF.at[i, c_uTo]))]
            
            for product, i_o in products:
    
                if i_o.startswith('i'):
                    self.inputs.add(product)
                elif i_o.startswith('o'):
                    self.outputs.add(product)
            
 
    def balance(self, product, qty, i_o, var_i='default', show='False'):
        """
        # product: final input or output on which to balance the calculations
        # qty: desired final quantity of product
        # i_o: whether product is an input (i) or output (o)
        # var_i: row index of variables files to use
        # show: whether to display the formatted inputs and outputs in the 
        # python terminal
        """

        #verify input
        if product not in self.inputs and product not in self.outputs:
            raise Exception('{} not found in {} input or output sets' \ 
                .format(product, self.name))

        if var_i not in self.varDF.index.values:
            raise Exception('{} not found in variables file'.format(var_i))

        if str.lower(i_o[0]) not in ['i', 'o', 't']:
            raise Exception('{} not valid product destination'.format(i_o))

        if product in lookupVar:
                product = self.varDF.at[var_i, lookupVar[product][1]]   
        
        logging.info("\nAttempting to balance {} on {} of {} ({}) using {} variables" \
            .format(self.name, qty, product, i_o, var_i))

        #setup function variables
        calcDF = self.calcDF
        ioDicts = {
            'i' : defaultdict(float),    # inputs dictionary
            'o' : defaultdict(float),    # outputs dictionary
            't' : defaultdict(float),    # temp dictionay (discarded values)
            'e' : defaultdict(float)     # emissions dictionary - adds value to output dictionary at end of function
        }
        # Add quantity of desired final product to appropriate dictionary (input or output)
        ioDicts[str.lower(i_o[0])][product] = qty
               
        #initalize counters for while counters
        i = 0
        attempt = 0
    
        # perform specified calculations, starting with the known substance
        while len(calcDF) > 0:
                       
            if i >= len(calcDF):     # if at end of list, loop around
                i = 0

            # setup loop variables
            known = calcDF.at[i, c_known]
            k_from =str.lower(calcDF.at[i, c_kFrom][0]) # shortens to i, o, or t (lower case)
            u_to = str.lower(calcDF.at[i, c_uTo][0]) # shortens to i, o or t (lower case)
            unknown = calcDF.at[i, c_unknown]
            calcType = str.lower(calcDF.at[i, c_calcType])
            invert = False
            var = False

            if str.lower(calcDF.at[i, c_var]) not in ignoreVar:
                var = self.varDF.at[var_i, calcDF.at[i, c_var]] 


            logging.info("current index: {}, current product: {}".format(i, known))

            if attempt >= len(calcDF):  # prevent infinite loops by terminating afer a complete loop through
                raise Exception("Cannot process {}". format(known))

            # check whether either quantity is a specified lookup variable,
            # and substitute from variable file, if so
            if known in lookupVar:
                known = self.varDF.at[var_i, lookupVar[known][1]] 
            if unknown in lookupVar:
                unknown = self.varDF.at[var_i, lookupVar[unknown][1]] 

            # Check that the specified "known" quantity exists in input/output dictionaries
            logging.info("checking for {} in {} dictionary".format(known,k_from))
            if known in ioDicts[k_from]:
                pass

            elif unknown in ioDicts[u_to]:
                logging.info("{} not found, but {} found. Inverting calculations" \ 
                    .format(known, unknown))
                invert = True
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                
            else:   #if substance isn't found start again from the beginning
                logging.info("neither {} nor {} found, skipping for now" \ 
                    .format(known, unknown))
                i += 1
                attempt += 1
                continue

            qtyKnown = ioDicts[k_from][known]
            logging.info("{} confirmed in {}s, qty: {}" \ 
                .format(known, ioDicts[k_from], qtyKnown))
            
            # performed specified calculation

            if calcType not in CalculationTypes:
                raise Exception("{} is an unknown calculation type".format(calcType))

            kwargs = dict(qty = qtyKnown, var = var, known = known, unknown = unknown, \
                invert = invert, emissionsDict = ioDicts['e'])
            qtyCalc = CalculationTypes[calcType](**kwargs)

            # assign calculated quantity to approproriate dictionary key
            if u_to not in ioDicts:
                raise Exception("{} is an unknown destination".format(u_to))
            
            ioDicts[u_to][unknown] += qtyCalc

            calcDF = calcDF.drop(i)
            calcDF = calcDF.reset_index(drop=True)

            logging.info("{} calculations remaining.".format(len(calcDF)))
            attempt = 0

            
        #add emissions dictionary to output dictionary
        for k, v in ioDicts['e'].items():
            ioDicts['o'][k] += v

        if show == True: # print inputs/outputs to terminal
            print("\n\n{} process balanced on {} of {}".format(self.name, qty, product))
           
            print('\nInputs:')
            for k, v in ioDicts['i'].items:
                print("{}: {}".format(k,v))
            
            print('\nOutputs:')
            for k, v in ioDicts['o'].items:
                print("{}: {}".format(k,v))

        #return dictionaries of inputs and outputs
        return ioDicts['i'], ioDicts['o']


class ProductChain:
    """
    Product chains are a linear sets of unit process linked by input and output; 
    the output of a unit process is the input into the next unit process.

    The product chain is balanced on a given output at the end of the chain
    or a given input at the beginning of a chain. Balancing a chain returns
    a nested dictionary with the total inputs and outputs, as well as the inputs
    and outputs of each unitProcess
    """

    def __init__(self, name, chainTSVorDF):
        self.name = name

        if isinstance(chainTSVorDF, pan.DataFrame):
            self.chainDF = chainTSVorDF
        else:
            self.chainDF = makeDF(chainTSVorDF)

        processList = False
    
    def checkFlow(self):
    """
    Checks the given flow to see if the specified flows exist in the appropriate
    output and input sets of the origin and destination unit processes.

    One end of the chain should specify "START" as the origin and the other
    end should have an "END" as a destination. 

    The output is a list of unit process objects, always in the order of
    START --> END  i.e. the output of a process is the input to the next
    process in the list.
    """
        processList = []

        if str.lower(flowDF.at[0, origin]) == 'start':
            self.i_o = "input based with {} to {} as default".format(flowDF.at[0, 'What'], flowDF.at[0, destination])

        # if the chain is written from end to start, reverse it
        elif str.lower(flowDF.at[0, destination]) == 'end':
            self.i_o = "output based with {} from {} as default".format(flowDF.at[0, 'What'], flowDF.at[0, destination])
            flowDF = flowDF[::-1]

        else:
            raise Exception("First line of flow must contain a 'start' in {} \
                or 'end' in {}.".format(origin, destination))
        
        for i in range(len(flowDF.index)):
            destination = unitProcess(flowDF.at[i, destination])
            output = flowDF.at[i, 'What']

            if i = 0:
                origin = False
                
            if i != 0
                if output not in origin.outputs:
                    raise Exception("{} not found in {} outputs".format\
                        (output, prevUnit.name))
                
                if output not found in destination.inputs:
                    raise Exception("{} not found in {} inputs".format\
                        (output, destination.name))       

            processList.append(origin, output) #unitProcess #output from process
            
            origin = destination       
            
            else:
                Raise Exception("Something went wrong.")

            self.processList = processList


    
    def balance(self, productQty, product=False, i_o= self.i_o , var_i="default", show = "False"):
    """

    """
        if self.processList == False:
            self.checkFlow()


        i_o = str.lower(i_o)[0]

        # Check that specify product exists, and ensure list of unit processes
        # are in calculation order 
        if i_o == "o":
            chain = self.processList.reverse()

            if product not in chain[0].outputs:
                raise Exception("{} not in {} outputs".format(product, chain[0].name))
        
        elif i_o == "i":
            chain = self.processList

            if product not in chain[0].inputs:
                raise Exception("{} not in {} inputs".format(product, chain[0].name))
        
        else:
            raise Exception("{} not found as input or output of chain.")


        # initalize return dictionaries
        inDict = ddict(lambda: ddict(float))
        outDict = ddict(lambda: ddict(float))

        ioDicts = {"i": inDict, "o": outDict}
        product = product
        qty = productQty      

        for unit in chain:
            inDict[unit.name], outDict[unit.name] = unit.balance(product, qty, i_o, var_i, show='False')
            product =  


        



    def diagram(self)
        if self.chainProcesses == False:
            self.checkFlow()