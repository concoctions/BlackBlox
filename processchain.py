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

    def __init__(self, chain_data, name="Product Chain", xls_sheet=None,):
        self.name = name

        self.process_chain_df = iof.check_if_df(chain_data, sheet=xls_sheet, index=None)

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
            if process_list[-1]['o'] in process_list[-1]['process'].outflows:
                self.default_product = process_list[-1]['o']

            elif process_list[0]['i'] in process_list[0]['process'].inflows:
                self.default_product = process_list[-1]['i']

            else:
                logger.debug(f"No default product found for {self.name}.")

    
    def balance(self, qty, product=False, i_o=False, var_i='default'):
        """

        """
        if not self.process_list:
            self.initialize_chain()

        chain = self.process_list.copy()

        if not product:
            product = self.default_product

        if i_o:
            i_o = iof.fl(i_o)
        
        if product in chain[-1]['process'].outflows and i_o != 'i':
            chain.reverse()
            i_o = 'o'
            io_opposite = 'i'


        elif product in chain[0]['process'].inflows and i_o != 'o':
            i_o = 'i'
            io_opposite = 'o'
        
        else:
            raise KeyError(f"{product} not found as input or outflow of chain.")

        io_dicts = {
            'i': defaultdict(lambda: defaultdict(float)), 
            'o': defaultdict(lambda: defaultdict(float))
            }

        intermediate_product_dict = defaultdict(float)

        # balancing individual unit processes in chain
        for i, unit in enumerate(chain):
            process = unit['process']

            if i != 0:
                product = unit[i_o]
                qty = io_dicts[io_opposite][previous_process.name][product]
                intermediate_product_dict[product] = qty

            logger.debug(f"balancing {process.name} on {qty} of {product}({i_o}) using {var_i} variables.")

            io_dicts['i'][process.name], io_dicts['o'][process.name] = process.balance(
             qty, product, i_o, var_i)

            previous_process = process

        if i_o == 'o':
            # as of python 3.7 dictionary iteration is guaranteed to be in insertion order
            # so reversing the dictionaries of output-based chains allows the dictionary
            # to be iterated in the order of chain processes.
            rev_inflows_dict = defaultdict(lambda: defaultdict(float))
            rev_outflows_dict = defaultdict(lambda: defaultdict(float))

            for p in self.process_list:
                rev_inflows_dict[p['process'].name] = io_dicts['i'][p['process'].name]
                rev_outflows_dict[p['process'].name] = io_dicts['o'][p['process'].name]
            
            io_dicts.clear()
            io_dicts['i'] = rev_inflows_dict
            io_dicts['o'] = rev_outflows_dict
            
        totals = {
            'i': defaultdict(float),
            'o': defaultdict(float)
            }

        for process, inflows_dict in io_dicts['i'].items():
            for inflow, qty in inflows_dict.items():
                totals['i'][inflow] += qty
    
        for process, outflows_dict in io_dicts['o'].items():
            for outflow, qty in outflows_dict.items():
                totals['o'][outflow] += qty

        for io_dict in totals:
            for product, qty in intermediate_product_dict.items():
                totals[io_dict][product] -= qty


        io_dicts['i']["chain totals"] = totals['i']
        io_dicts['o']["chain totals"] = totals['o']
        
        return io_dicts['i'], io_dicts['o']


    def diagram(self, view_diagram=True, return_diagram=False):

        c = self.name

        if not self.process_list:
            self.initialize_chain()

        chain_diagram = Digraph(name=self.name, directory='outputFiles/pfd/chains', format='png')
        product_flow = Digraph('mainflow_'+self.name)
        product_flow.graph_attr.update(rank='same')
        product_flow.attr('node', shape='box')
        chain_diagram.attr('node', shape='box')

        for i, unit in enumerate(self.process_list):
            name = unit['process'].name
            inflows = '\n'.join(unit['process'].inflows)
            outflows = '\n'.join(unit['process'].outflows)

            if i == 0:
                chain_diagram.node(c+name+inflows, label=inflows, color='white')
                product_flow.node(c+name, label=name)
                chain_diagram.edge(c+name+inflows, c+name)

                if len(self.process_list) == 1:
                    chain_diagram.node(c+name+outflows, label=outflows, color='white')
                    chain_diagram.edge(c+name, c+name+outflows)

                elif outflows != unit['o']:
                    outflows = outflows.replace(unit['o'], '')
                    if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                    chain_diagram.node(c+name+outflows, label=outflows, color='white')
                    chain_diagram.edge(c+name, c+name+outflows)


            elif i < len(self.process_list) - 1:
                product_flow.node(c+name, label=name)
                product_flow.edge(c+prevunit, c+name, label=unit['i'])

                if inflows != unit['i']:
                    inflows = inflows.replace(unit['i'], '')
                    if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                    chain_diagram.node(c+name+inflows, label=inflows, color='white')
                    chain_diagram.edge(c+name+inflows, c+name)

                if outflows != unit['o']:
                    outflows = outflows.replace(unit['o'], '')
                    if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                    chain_diagram.node(c+name+outflows, label=outflows, color='white')
                    chain_diagram.edge(c+name, c+name+outflows)

            else:
                product_flow.node(c+name, label=name)
                product_flow.edge(c+prevunit, c+name, label=unit['i'])

                if inflows != unit['i']:
                    inflows = inflows.replace(unit['i'], '')
                    if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                    chain_diagram.node(c+name+inflows, label=inflows, color='white')
                    chain_diagram.edge(c+name+inflows, c+name)

                chain_diagram.node(c+name+outflows, label=outflows, color='white')
                chain_diagram.edge(c+name, c+name+outflows)

            prevunit = name

        chain_diagram.subgraph(product_flow)

        if view_diagram is True:
            chain_diagram.view()


        chain_diagram.format = 'svg'
        chain_diagram.render()

        if return_diagram:
            return product_flow
