import pandas as pan
from molmass import Formula
from collections import defaultdict
from io_functions import *
from dataconfig import *
from calculators import *
from unitprocess import *
from bb_log import get_logger

logger = get_logger("Multi Process")

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

        self.process_chain_df = check_if_df(chain_data, index=None)

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
                logger.info(f"No default product found for {self.name}.")

    
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

            logger.info(f"balancing {process.name} on {product_qty} of {product}({i_o}) using {var_i} variables.")

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



# class Factory:
#     """
#     Factories are made up of one or more product chains, and balance on a specified
#     output product. Product chains that are not the main output product balance
#     on the relevent inputs and outputs of the main product. All product chains in
#     a factory should be run using variables from the same scenario
#     """

#     def __init__(self, factory_data, name="Factory"):
#         self.name = name

#         self.factory_df = check_if_df(chain_data, index=None)
   
#         self.default_product = False
#         self.chain_list = False

#     def initalize_factory(self):

#     def run_scenarios(self, scenario_list=[default_scenario]):

#     def diagram(self):


# class Industry:
#     """
#     Industries are made up of one or more factories, and are balanced on one or more
#     factory products. Factories within an industry can run with different scenario
#     data. Industries can change over time.
#     """

#     def __init__(self, industry_data, name='Industry'):

#     def run_scenarios(self, scenario_list=[default_scenario]):

#     def evolve(self, start_scenarios, end_scenarios):

    
