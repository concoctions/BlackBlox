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
    a factory should be run using variables from the same scenario.
    """

    def __init__(self, factory_chains_data, factory_connections_data, name="Factory"):
        self.name = name
        self.chains_df = iof.check_if_df(factory_chains_data, index=None)
        self.connections_df = iof.check_if_df(factory_connections_data, index=None)
        self.main_chain = False
        self.chain_dict = False

    def initalize_factory(self):
        logger.debug(f"initializing factory for {self.name}")
        
        chain_dict = defaultdict(dict)

        for i, c in self.chains_df.iterrows():
            name = c[dat.chain_name] 
            if i == 0:
                self.main_chain = name
                
            chain_dict[name] = dict(chain=cha.ProductChain(c[dat.chain_filepath], name), 
                                    name=name, product=c[dat.chain_product], 
                                    i_o=str.lower(c[dat.chain_io][0]))

        self.chain_dict = chain_dict

    def balance(self, main_product_qty, var_i=dat.default_scenario):
        if not self.chain_dict:
            self.initalize_factory()

        logger.debug(f"balancing factory on {main_product_qty} of {self.chain_dict[self.main_chain]['product']}")

        io_dicts = {
            'i': defaultdict(lambda: defaultdict(lambda: defaultdict(float))), 
            'o': defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
            }

        intermediate_product_dict = defaultdict(float)
           

        m = self.chain_dict[self.main_chain]
        
        io_dicts['i'][m['name']], io_dicts['o'][m['name']] = m['chain'].balance(
            main_product_qty, product= m['product'], var_i=var_i)

        for i, c in self.connections_df.iterrows():    
            qty = False
            i_io = str.lower(c[dat.origin_io][0])
            d_io = str.lower(c[dat.destination_io][0])

            if c[dat.origin_chain] == dat.connect_all:
                pass
                
            else:
                o = self.chain_dict[c[dat.origin_chain]]
                d = self.chain_dict[c[dat.dest_chain]]
                product = c[dat.connect_product]

                if c[dat.origin_process] == dat.connect_all:
                        qty = io_dicts[i_io][o['name']]['chain totals'][product]

                else:
                    o_unit = c[dat.origin_process]
                    qty = io_dicts[i_io][o['name']][o_unit][product]
                
                intermediate_product_dict[product] += qty
                
                print(f"{qty} of {product} as product from {o['name']} ({i_io}) to {d['name']} ({d_io})")

                i_tmp, o_tmp = d['chain'].balance(qty, product=product, i_o=d_io, var_i=var_i)

                if io_dicts['i'][d['name']] and io_dicts['o'][d['name']]:
                    
                    for process_dict in i_tmp:
                        for substance, qty in i_tmp[process_dict].items():
                            io_dicts['i'][d['name']][process_dict][substance] += qty

                    for process_dict in o_tmp:
                        for substance, qty in o_tmp[process_dict].items():
                            io_dicts['o'][d['name']][process_dict][substance] += qty

                else:    
                    io_dicts['i'][d['name']], io_dicts['o'][d['name']] = i_tmp, o_tmp 

                

        totals = {
            'i': defaultdict(float),
            'o': defaultdict(float)
            }

        for chain_dict in io_dicts['i']:
            for inflow, qty in io_dicts['i'][chain_dict]['chain totals'].items():
                totals['i'][inflow] += qty
    
        for chain_dict in io_dicts['o']:
            for outflow, qty in io_dicts['o'][chain_dict]['chain totals'].items():
                totals['o'][outflow] += qty

        for io_dict in totals:
            for product, qty in intermediate_product_dict.items():
                print(product, qty)
                totals[io_dict][product] -= qty

        io_dicts['i']["factory inflows"]['factory totals'] = totals['i']
        io_dicts['o']["factory outflows"]['factory totals'] = totals['o']
        
        return io_dicts['i'], io_dicts['o']


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

