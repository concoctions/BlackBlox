import pandas as pan
from molmass import Formula
from collections import defaultdict
from io_functions import makeDF
from dataconfig import *
from calculators import *
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

    def __init__(self, name, variables_df=False, calculations_df=False, unit_processes_df=df_unit_processes):
        self.name = name

        if isinstance(variables_df, pan.DataFrame):
            self.variables_df = variables_df
        else:
            self.variables_df = makeDF(unit_processes_df.at[name, variables_filepath_col])

        if isinstance(calculations_df, pan.DataFrame):
            self.calculations_df = calculations_df
        
        else:
            self.calculations_df = makeDF(unit_processes_df.at[name, calculations_filepath_col], index=None)

        #create sets of process inflows and outflows
        self.default_product = unit_processes_df.at[name,default_product_col]
        self.default_io = unit_processes_df.at[name,default_product_io_col]
        
        self.inflows = set() 
        self.outflows = set() 

        
        for i in self.calculations_df.index: 
            products = [ (self.calculations_df.at[i, known_substance_col], str.lower(self.calculations_df.at[i, known_io_col])),\
                 (self.calculations_df.at[i, unknown_substance_col],str.lower(self.calculations_df.at[i, unknown_io_col]))]
            
            for product, i_o in products:
    
                if i_o.startswith('i'):
                    self.inflows.add(product)
                elif i_o.startswith('o'):
                    self.outflows.add(product)
            
 
    def balance(self, qty, product=False, i_o=False, 
        var_i=False, show=False):
        """
        # product: final input or outflow on which to balance the calculations
        # qty: desired final quantity of product
        # i_o: whether product is an input (i) or outflow (o)
        # var_i: row index of variables files to use
        # show: whether to display the formatted inflows and outflows in the 
        # python terminal
        """

        if product is False:
            product = self.default_product
        if i_o is False:
            i_o = self.default_io
        if var_i is False:
            var_i = default_scenario

        #verify input
        if product not in self.inflows and product not in self.outflows:
            raise Exception(f'{product} not found in {self.name} inflows or outflows')

        if var_i not in self.variables_df.index.values:
            raise Exception(f'{var_i} not found in variables file')

        if str.lower(i_o[0]) not in ['i', 'o', 't']:
            raise Exception(f'{i_o} not valid product destination')

        if product in lookup_variables_dict:
                product = self.variables_df.at[var_i, lookup_variables_dict[product]['lookup_var']]   
        
        logging.info(f"\nAttempting to balance {self.name} on {qty} of {product} ({i_o}) using {var_i} variables")

        #setup function variables
        calculations_df = self.calculations_df
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
    
        # perform specified calculations, starting with the known_substance
        while len(calculations_df) > 0:
                       
            if i >= len(calculations_df):     # if at end of list, loop around
                i = 0

            # setup loop variables
            known_substance = calculations_df.at[i, known_substance_col]
            known_io =str.lower(calculations_df.at[i, known_io_col][0]) # shortens to i, o, or t (lower case)
            unknown_io = str.lower(calculations_df.at[i, unknown_io_col][0]) # shortens to i, o or t (lower case)
            unknown_substance = calculations_df.at[i, unknown_substance_col]
            calculation_type = str.lower(calculations_df.at[i, calculation_type_col])
            invert = False
            var = False

            if str.lower(calculations_df.at[i, variable_col]) not in variables_to_ignore:
                var = self.variables_df.at[var_i, calculations_df.at[i, variable_col]] 


            logging.info(f"current index: {i}, current product: {known_substance}")

            if attempt >= len(calculations_df):  # prevent infinite loops by terminating afer a complete loop through
                raise Exception(f"Cannot process {known_substance}")

            # check whether either quantity is a specified lookup variable,
            # and substitute from variable file, if so
            if known_substance in lookup_variables_dict:
                known_substance = self.variables_df.at[var_i, lookup_variables_dict[known_substance]['lookup_var']] 
            if unknown_substance in lookup_variables_dict:
                unknown_substance = self.variables_df.at[var_i, lookup_variables_dict[unknown_substance]['lookup_var']] 

            # Check that the specified "known_substance" quantity exists in input/outflow dictionaries
            if known_substance in io_dicts[known_io]:
                pass

            elif unknown_substance in io_dicts[unknown_io]:
                invert = True
                known_substance, unknown_substance = unknown_substance, known_substance
                known_io, unknown_io = unknown_io, known_io
                logging.info(f"{known_substance} not found, but {unknown_substance} found. Inverting calculations")

                
            else:   #if substance isn't found start again from the beginning
                i += 1
                attempt += 1
                logging.info(f"neither {known_substance} nor {unknown_substance} found, skipping for now")
                continue


            
            # performed specified calculation
            qty_known = io_dicts[known_io][known_substance]

            if calculation_type not in calculation_types_dict:
                raise Exception(f"{calculation_type} is an unknown_substance calculation type")

            kwargs = dict(qty=qty_known, var=var, known_substance=known_substance, unknown_substance=unknown_substance,
                invert=invert, emissions_dict=io_dicts['e'])
                
            qty_calculated = calculation_types_dict[calculation_type](**kwargs)

            # assign calculated quantity to approproriate dictionary key
            if unknown_io not in io_dicts:
                raise Exception("{} is an unknown_substance destination".format(unknown_io))
            
            io_dicts[unknown_io][unknown_substance] += qty_calculated

            calculations_df = calculations_df.drop(i)
            calculations_df = calculations_df.reset_index(drop=True)

            logging.info("{} calculations remaining.".format(len(calculations_df)))
            attempt = 0

            
        #add emissions dictionary to outflow dictionary
        for substance, qty in io_dicts['e'].items():
            io_dicts['o'][substance] += qty

        if show is True: # print inflows/outflows to terminal
            print(f"\n\n{self.name} process balanced on {qty} of {product}")
           
            print('\nInflows:')
            for substance, qty in io_dicts['i'].items():
                print(f"{substance}: {qty}")
            
            print('\nOutflows:')
            for substance, qty in io_dicts['o'].items():
                print(f"{substance}: {qty}")

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

    def __init__(self, chain_data, name="Product Chain"):
        self.name = name

        if isinstance(chain_data, pan.DataFrame):
            self.process_chain_df = chain_data
        else:
            self.process_chain_df = makeDF(chain_data, index=None)

        self.default_product = False
        self.process_list = False
    
    def initialize_chain(self):
        """
        Checks the given process chain to ensure that the inflows and outflows
        specified exist in the corresponding unit processes.
        """
        process_list = []

        for index, process_row in self.process_chain_df.iterrows():
            process = UnitProcess(process_row[process_col])
            inflow = process_row[inflow_col]
            outflow = process_row[outflow_col]

            if inflow not in process.inflows and index != 0:
                raise KeyError(f"{inflow} not found in {process.name} inflows")            
            
            if outflow not in process.outflows and index !=self.process_chain_df.index[-1]:
                raise KeyError(f"{outflow} not found in {process.name} outflows")
 
            process_list.append(dict(process=process, i=inflow, o=outflow))
            
        self.process_list = process_list

        if not self.default_product:
            if process_list[-1]["o"] in process_list[-1]["process"].outflows:
                self.default_product = process_list[-1]["o"]

            elif process_list[0]["i"] in process_list[0]["process"].inflows:
                self.default_product = process_list[-1]["i"]

            else:
                logging.info(f"No default product found for {self.name}.")

    
    def balance(self, product_qty, product=False,
                var_i="default"):
        """

        """
        if not self.process_list:
            self.initialize_chain()

        chain = self.process_list

        if not product:
            product = self.default_product

        if product in self.process_list[0]['process'].inflows:
            i_o = "i"
            io_opposite = "o"

        elif product in self.process_list[-1]['process'].outflows:
            chain.reverse()
            i_o = "o"
            io_opposite = "i"
        
        else:
            raise KeyError(f"{product} not found as input or outflow of chain.")

        io_dicts = {
            "i": defaultdict(lambda: defaultdict(float)), 
            "o": defaultdict(lambda: defaultdict(float))
            }

        # balancing individual unit processes in chain
        for i, unit in enumerate(chain):
            process = unit['process']
            print(f"balancing {process.name}")

            if i != 0:
                product = unit[i_o]
                product_qty = io_dicts[io_opposite][previous_process.name][product]

            logging.info(f"balancing {process.name} on {product_qty} of {product}({i_o}) using {var_i} variables.")

            io_dicts["i"][process.name], io_dicts["o"][process.name] = process.balance(
             product_qty, product, i_o, var_i)

            previous_process = process

        totals = {
            "i": defaultdict(float),
            "o": defaultdict(float)
            }

        for process, inflows_dict in io_dicts["i"].items():
            for inflow, qty in inflows_dict.items():
                totals["i"][inflow] += qty
    
        for process, outflows_dict in io_dicts["o"].items():
            for outflow, qty in outflows_dict.items():
                totals["o"][outflow] += qty

        for i, unit in enumerate(chain): # removes intermediate products
            process = unit['process']

            if i != 0:
                intermediate_product = unit[io_opposite]
                totals[io_opposite][intermediate_product] -= io_dicts[io_opposite][process.name][intermediate_product]

            if i != len(chain) - 1:
                intermediate_product = unit[i_o]
                totals[i_o][intermediate_product] -= io_dicts[i_o][process.name][intermediate_product]


        io_dicts["i"]["chain inputs"] = totals["i"]
        io_dicts["o"]["chain outputs"] = totals["o"]
        
        return io_dicts


    # def diagram(self):

    #     if not self.chainProcesses:
    #         self initialize_chain()