import pandas as pan
from molmass import Formula
from collections import defaultdict
from graphviz import Digraph

from bb_log import get_logger

import io_functions as iof
import dataconfig as dat
import calculators as calc
import unitprocess as unit
import processchain as cha


logger = get_logger("Factory")

class Factory:
    """
    Factories are made up of one or more product chains, and balance on a specified
    output product. Product chains that are not the main output product balance
    on the relevent inputs and outputs of the main product. All product chains in
    a factory should be run using variables from the same scenario
    """

    def __init__(self, factory_chains_data, factory_connections_data, name="Factory"):
        self.name = name
        self.chains_df = iof.check_if_df(factory_chains_data)
        self.connections_df = iof.check_if_df(factory_connections_data, index=None)
        self.chain_dict = False

    def initalize_factory(self):
        logger.debug(f"initializing factory for {self.name}")
        
        chain_dict = defaultdict(dict)

        for chain_name, chain_row in self.chains_df.iterrows(): 
            if chain_row[dat.chain_product] == dat.main_chain:
                if chain_dict['main']:
                    raise Exception("Only one chain is allowed")
                else:
                    chain_dict['main'] = dict(chain=cha.ProductChain(chain_row[dat.chain_filepath], 
                                 chain_name), name=chain_name,
                                 type=chain_row[dat.chain_product], product=chain_row[dat.chain_product],
                                 i_o=str.lower(chain_row[dat.chain_io][0]))

            else:
                chain_dict[chain_name] = dict(chain=cha.ProductChain(chain_row[dat.chain_filepath], 
                                 chain_name), name=chain_name,
                                 type=chain_row[dat.chain_product], product=chain_row[dat.chain_product],
                                 i_o=str.lower(chain_row[dat.chain_io][0]))

        self.chain_dict = chain_dict

    def balance(self, main_product_qty, var_i=dat.default_scenario):
        if not self.chain_dict:
            self.initalize_factory()

        logger.debug(f"balancing factory on {main_product_qty} of {self.chain_dict['main']['product']}")

        io_dicts = {
            "i": defaultdict(lambda: defaultdict(lambda: defaultdict(float))), 
            "o": defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
            }

        c = self.chain_dict['main']
        io_dicts['i'][c['name']], io_dicts['o'][c['name']] = c['chain'].balance(
            main_product_qty, var_i)

        for i, e in self.connections_df:    # e for edge
            product_qty = False
            product_io = str.lower(e[dat.connect_io][0])

            if e[dat.origin_chain] == dat.connect_all:
                pass
            else:
                o = self.chain_dict[e[dat.origin_chain]]
                d = self.chain_dict[e[dat.dest_chain]]
                if e[dat.origin_process] == dat.connect_all:
                    pass
                else:
                    product_qty = io_dicts[product_io][dat.origin_chain][dat.origin_process][dat.connect_product]
                    io_dicts['i'][c['name']], io_dicts['o'][c['name']] = c['chain'].balance(
                    product_qty, var_i)





    # def run_scenarios(self, scenario_list=[default_scenario]):

    # def diagram(self):


# class Industry:
#     """
#     Industries are made up of one or more factories, and are balanced on one or more
#     factory products. Factories within an industry can run with different scenario
#     data. Industries can change over time.
#     """

#     def __init__(self, industry_data, name='Industry'):

#     def run_scenarios(self, scenario_list=[default_scenario]):

#     def evolve(self, start_scenarios, end_scenarios):

