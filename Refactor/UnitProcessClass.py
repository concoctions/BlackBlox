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
    UnitProcess objects have a set of inflows and outflows, with the relationship 
    between them expressed in a DataFrame of calculations and a DataFrame of 
    variables to use in the calculations.

    The sets of inflows and outflows is derived from the list of calculation 
    supplied by the user.

    UnitProcess.balance allows the user to specify a specific quantity of an 
    input and , and a specific set of calculation variables to use, and the 
    function will return dictionaries (defaultdict) of the quantities of the 
    unit process inflows and outflows to balance the given product quantity.
    """

    def __init__(self, name, varDF=False, calcDF=False, unitListDF=False):
        self.name = name

        if isinstance(varDF, pan.DataFrame):
            self.varDF = varDF
        else:
            self.varDF = makeDF(df_unitList.at[name,ul_varFileLoc])

        if isinstance(calc, pan.DataFrame):
            self.calcDF = calcDF
        self.calcDF = makeDF(df_unitList.at[name,ul_calcFileLoc], index=None)

        #create sets of process inflows and outflows
        self.inflows = set() 
        self.outflows = set() 

        
        for i in self.calcDF.index: 

            # list of tuples of the known/unknown products
            # and whether they are process inflows or outflows  
            products = [ (self.calcDF.at[i, c_known], str.lower(self.calcDF.at[i, c_kFrom])),\
                 (self.calcDF.at[i, c_unknown],str.lower(self.calcDF.at[i, c_uTo]))]
            
            for product, i_o in products:
    
                if i_o.startswith('i'):
                    self.inflows.add(product)
                elif i_o.startswith('o'):
                    self.outflows.add(product)
            
 
    def balance(self, product, qty, i_o, var_i='default', show='False'):
        """
        # product: final input or outflow on which to balance the calculations
        # qty: desired final quantity of product
        # i_o: whether product is an input (i) or outflow (o)
        # var_i: row index of variables files to use
        # show: whether to display the formatted inflows and outflows in the 
        # python terminal
        """

        #verify input
        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{product} not found in {self.name} input or outflow sets')

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
        io_dicts = {
            'i' : defaultdict(float),    # inflows dictionary
            'o' : defaultdict(float),    # outflows dictionary
            't' : defaultdict(float),    # temp dictionay (discarded values)
            'e' : defaultdict(float)     # emissions dictionary - adds value to outflow dictionary at end of function
        }
        # Add quantity of desired final product to appropriate dictionary (input or outflow)
        io_dicts[str.lower(i_o[0])][product] = qty
               
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

            # Check that the specified "known" quantity exists in input/outflow dictionaries
            logging.info("checking for {} in {} dictionary".format(known,k_from))
            if known in io_dicts[k_from]:
                pass

            elif unknown in io_dicts[u_to]:
                logging.info(f"{known} not found, but {unknown} found. Inverting calculations")
                invert = True
                known, unknown = unknown, known
                k_from, u_to = u_to, k_from
                
            else:   #if substance isn't found start again from the beginning
                logging.info(f"neither {known} nor {unknown} found, skipping for now")
                i += 1
                attempt += 1
                continue

            qtyKnown = io_dicts[k_from][known]
            logging.info(f"{known} confirmed in {io_dicts[k_from]}s, qty: {qtyKnown}")
            
            # performed specified calculation

            if calcType not in CalculationTypes:
                raise Exception("{} is an unknown calculation type".format(calcType))

            kwargs = dict(qty=qtyKnown, var=var, known=known, unknown=unknown,
                invert=invert, emissionsDict=io_dicts['e'])
            qtyCalc = CalculationTypes[calcType](**kwargs)

            # assign calculated quantity to approproriate dictionary key
            if u_to not in io_dicts:
                raise Exception("{} is an unknown destination".format(u_to))
            
            io_dicts[u_to][unknown] += qtyCalc

            calcDF = calcDF.drop(i)
            calcDF = calcDF.reset_index(drop=True)

            logging.info("{} calculations remaining.".format(len(calcDF)))
            attempt = 0

            
        #add emissions dictionary to outflow dictionary
        for k, v in io_dicts['e'].items():
            io_dicts['o'][k] += v

        if show == True: # print inflows/outflows to terminal
            print("\n\n{} process balanced on {} of {}".format(self.name, qty, product))
           
            print('\nInflows:')
            for k, v in io_dicts['i'].items:
                print("{}: {}".format(k,v))
            
            print('\nOutflows:')
            for k, v in io_dicts['o'].items:
                print("{}: {}".format(k,v))

        #return dictionaries of inflows and outflows
        return io_dicts['i'], io_dicts['o']


class ProductChain:
    """
    Product chains are a linear sets of unit process linked by input and outflow; 
    the outflow of a unit process is the input into the next unit process.

    The product chain is balanced on a given outflow at the end of the chain
    or a given input at the beginning of a chain. Balancing a chain returns
    a nested dictionary with the total inflows and outflows, as well as the inflows
    and outflows of each unitProcess
    """

    def __init__(self, name, chain_data):
        self.name = name

        if isinstance(chain_data, pan.DataFrame):
            self.chainDF = chain_data
        else:
            self.chainDF = makeDF(chain_data)

        process_list = False
    
    def checkFlow(self):
        """
        Checks the given flow to see if the specified flows exist in the appropriate
        outflow and input sets of the origin and destination unit processes.

        One end of the chain should specify "START" as the origin and the other
        end should have an "END" as a destination. 

        The outflow is a list of unit process objects, always in the order of
        START --> END  i.e. the outflow of a process is the input to the next
        process in the list.
        """
        process_list = []

        self.product = self.chainDF.at[0, what]

        if str.lower(self.chainDF.at[0, origin]) == 'start':
            self.i_o = (f"inflow based, balancing on {self.product}")

        # if the chain is written from end to start, reverse it
        elif str.lower(self.chainDF.at[0, destination]) == 'end':
            self.i_o = (f"outflow based, balancing on {self.product}")

            self.chainDF = self.chainDF[::-1]

        else:
            raise Exception(f"First line of flow must contain a 'start' in {origin}",
             "or 'end' in {destination}.")
        
        for i in range(len(self.chainDF.index)):
            destination = unitProcess(self.chainDF.at[i, destination])
            outflow = self.chainDF.at[i, what]

            if i == 0:
                pass
                
            elif i != 0:
                if outflow not in origin.outflows:
                    raise KeyError(f"{outflow} not found in {origin.name} outflows")
                
                if outflow not in destination.inflows:
                    raise KeyError(f"{outflow} not found in {destination.name} inflows".format\

                process_list.append(dict(process=origin, i=inflow, o=outflow))

            else:
                Raise Exception("Something went wrong.")                
            
            origin = destination
            inflow = outflow      
            

            self.process_list = process_list


    
    def balance(self, product_qty, product=self.product, i_o=self.i_o, 
                var_i="default", show="False"):
    """

    """
        if not self.process_list:
            self.checkFlow()

        i_o = str.lower(i_o)[0]

        if i_o is "o":
            chain = self.process_list.reverse()
            io_opposite = "i"

            if product not in chain[0].outflows:
                raise KeyError("{} not in {} outflows".format(product, chain[0].name))
        
        elif i_o is "i":
            chain = self.process_list
            io_opposite = "o"

            if product not in chain[0].inflows:
                raise KeyError(f"{product} not in {chain[0].name} inflows")
        
        else:
            raise KeyError("{} not found as input or outflow of chain.")


        io_dicts = {
            "i": ddict(lambda: ddict(float), 
            "o": ddict(lambda: ddict(float)
            }

        # balancing individual unit processes in chain
        for i, process in enumerate(chain):
            unit = process["process"]

            if i != 0:
                product = process[i_o]
                product_qty = io_dicts[io_opposite][previous_unit][product]

            logging.info(f"balancing {unit.name} on {product_qty} of {product}({i_o}) using {var_i} variables.")

            io_dicts["i"][unit.name], io_dicts["o"][unit.name] = unit.balance(
             product, product_qty, i_o, var_i)

             previous_unit = unit

        total_inflows = ddict(float)

        for process, inflows_dict in io_dicts["i"].items():
            for inflow, qty in inflows_dict.items():
                total_inflows[inflow] += qty

        total_outflows = ddict(float)
    
        for process, outflows_dict in io_dicts["o"].items():
            for outflow, qty in outflows_dict.items():
                total_outflows[outflow] += qty

        for process in chain[1:-1]:








        

        return(io_dicts)

            

           




    def diagram(self)
        if not self.chainProcesses:
            self.checkFlow()