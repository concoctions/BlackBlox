import pandas as pan
from molmass import Formula
from collections import defaultdict
from graphviz import Digraph

from bb_log import get_logger

import io_functions as iof
import dataconfig as dat
import calculators as calc
import unitprocess as unit


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

        self.process_chain_df = iof.check_if_df(chain_data, index=None)

        self.default_product = False
        self.process_list = False
    
    def initialize_chain(self):
        """
        Checks the given process chain to ensure that the inflows and outflows
        specified exist in the corresponding unit processes.
        """
        logger.debug(f"initializing chain for {self.name}")
        process_list = []

        for index, process_row in self.process_chain_df.iterrows():
            process = unit.UnitProcess(process_row[dat.process_col])
            inflow = process_row[dat.inflow_col]
            outflow = process_row[dat.outflow_col]

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
                logger.debug(f"No default product found for {self.name}.")

    
    def balance(self, product_qty, product=False, var_i="default"):
        """

        """
        if not self.process_list:
            self.initialize_chain()

        chain = self.process_list.copy()

        if not product:
            product = self.default_product

        
        if product in chain[-1]['process'].outflows:
            chain.reverse()
            i_o = "o"
            io_opposite = "i"


        elif product in chain[0]['process'].inflows:
            i_o = "i"
            io_opposite = "o"
        
        else:
            raise KeyError(f"{product} not found as input or outflow of chain.")

        io_dicts = {
            "i": defaultdict(lambda: defaultdict(float)), 
            "o": defaultdict(lambda: defaultdict(float))
            }

        # balancing individual unit processes in chain
        for i, unit in enumerate(chain):
            process = unit['process']

            if i != 0:
                product = unit[i_o]
                product_qty = io_dicts[io_opposite][previous_process.name][product]

            logger.debug(f"balancing {process.name} on {product_qty} of {product}({i_o}) using {var_i} variables.")

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
                intermediate_product = unit[i_o]
                totals[i_o][intermediate_product] -= io_dicts[i_o][process.name][intermediate_product]

            if i != len(chain) - 1:
                intermediate_product = unit[io_opposite]
                totals[io_opposite][intermediate_product] -= io_dicts[io_opposite][process.name][intermediate_product]


        io_dicts["i"]["chain inputs"] = totals["i"]
        io_dicts["o"]["chain outputs"] = totals["o"]
        
        return io_dicts


    def diagram(self):

        if not self.process_list:
            self.initialize_chain()

        diagram = Digraph(name=self.name, directory='outputFiles', format='png')
        product_flow = Digraph('mainflow')
        product_flow.graph_attr.update(rank='same')
        product_flow.attr('node', shape='box', style='', color='', fontcolor='')
        diagram.attr('node', shape='box')

        for i, unit in enumerate(self.process_list):
            inflows = '\n'.join(unit['process'].inflows)
            outflows = '\n'.join(unit['process'].outflows)

            if i == 0:
                product_flow.node(inflows, color='white')
                product_flow.node(unit['process'].name)
                product_flow.edge(inflows, unit['process'].name)

                if len(self.process_list) == 1:
                    product_flow.node(outflows, color='white')
                    product_flow.edge(unit['process'].name, outflows)

                elif outflows != unit['o']:
                    if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                    outflows = outflows.replace(unit['o'], '')
                    diagram.node(outflows, color='white', fontcolor='grey')
                    diagram.edge(unit['process'].name, outflows)


            elif i < len(self.process_list) - 1:
                product_flow.node(unit['process'].name)
                product_flow.edge(prevunit['process'].name, unit['process'].name, label=unit['i'])

                if inflows != unit['i']:
                    inflows = inflows.replace(unit['i'], '')
                    if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                    diagram.node(inflows, color='white', fontcolor='grey')
                    diagram.edge(inflows, unit['process'].name, color='grey')

                if outflows != unit['o']:
                    outflows = outflows.replace(unit['o'], '')
                    if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                    diagram.node(outflows, color='white', fontcolor='grey')
                    diagram.edge(unit['process'].name, outflows, color='grey')

            else:
                product_flow.node(unit['process'].name)
                product_flow.edge(prevunit['process'].name, unit['process'].name, label=unit['i'])

                if inflows != unit['i']:
                    inflows = inflows.replace(unit['i'], '')
                    if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                    diagram.node(inflows, color='white', fontcolor='grey')
                    diagram.edge(inflows, unit['process'].name, color='grey')

                product_flow.node(outflows, color='white')
                product_flow.edge(unit['process'].name, outflows)

            prevunit = unit

            
        diagram.subgraph(product_flow)
        diagram.view()

        diagram.format = 'svg'
        diagram.render()
