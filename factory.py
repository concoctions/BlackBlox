import pandas as pan
from molmass import Formula
from collections import defaultdict
from graphviz import Digraph
from datetime import datetime

from bb_log import get_logger

import io_functions as iof
import dataconfig as dat
import calculators as calc
import unitprocess as unit
import processchain as cha


logger = get_logger("Factory")

class Factory:
    """Factories are groups of one or more connected process chains

    Factories balance on a specified output product. Product chains that 
    are not the main output product balance on the relevent inputs and 
    outputs of the main product. All product chains in a factory are run 
    using variables from the same scenario.

    Args:
        chains_file: Table detailing the chains used in the factory. 
            Must contain columns for:
            [Chain Name, Chain Product, Product_IO, ChainFile]
        connections_file: Table detailing the connections between
            chains in the factory. Must contain data for:
            [OriginChain, OriginProcess, Product, Product_IO_of_Origin, 
            Product_IO_of_Destination, DestinationChain]    
        name (str, optional): The name of the factory. Defaults to False.

    Attributes:
        name
        chains_df
        connections_df
        main_chain
        chain_dict
    """

    def __init__(self, chains_file, connections_file, chains_sheet=None, 
                 connections_sheet=None, name="Factory"):
        self.name = name
        self.chains_df = iof.check_if_df(chains_file, chains_sheet, index=None)
        self.connections_df = iof.check_if_df(connections_file, connections_sheet, index=None)
        self.main_chain = False
        self.chain_dict = False

    def initalize_factory(self):
        logger.debug(f"initializing factory for {self.name}")
        
        chain_dict = defaultdict(dict)

        for i, c in self.chains_df.iterrows():
            name = c[dat.chain_name] 
            if i == 0:
                self.main_chain = name
            
            chain_sheet = iof.check_sheet(self.chains_df, dat.chain_sheetname, i)
 
                
            chain_dict[name] = dict(chain=cha.ProductChain(c[dat.chain_filepath], 
                                    name=name, xls_sheet=chain_sheet), 
                                    name=name, 
                                    product=c[dat.chain_product], 
                                    i_o=iof.fl(c[dat.chain_io]))

        self.chain_dict = chain_dict

    def balance(self, main_product_qty, var_i=dat.default_scenario, write_to_xls=True):
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

        for dummy_index, c in self.connections_df.iterrows():    
            qty = False
            o_io = iof.fl(c[dat.origin_io])
            d_io = iof.fl(c[dat.dest_io])

            if c[dat.origin_chain] == dat.connect_all:
                pass
                
            else:
                o = self.chain_dict[c[dat.origin_chain]]
                d = self.chain_dict[c[dat.dest_chain]]
                product = c[dat.connect_product]

                if c[dat.origin_process] == dat.connect_all:
                        qty = io_dicts[o_io][o['name']]['chain totals'][product]

                else:
                    o_unit = c[dat.origin_process]
                    qty = io_dicts[o_io][o['name']][o_unit][product]
                
                intermediate_product_dict[product] += qty
                
                logger.debug(f"{qty} of {product} as product from {o['name']} ({o_io}) to {d['name']} ({d_io})")

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

        io_dicts['i']['factory inflows']['factory totals'] = totals['i']
        io_dicts['o']['factory outflows']['factory totals'] = totals['o']

        if write_to_xls is True:
            filename = f'f_{self.name}_{var_i}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

            totals = defaultdict(lambda: defaultdict(float))
            totals['factory inflows'] = io_dicts['i']['factory inflows']['factory totals']
            totals['factory outflows'] = io_dicts['o']['factory outflows']['factory totals']
            totalsDF = pan.DataFrame(totals)

            df_list = [totalsDF]
            sheet_list = [f'{self.name} totals']

            all_inflows = defaultdict(lambda: defaultdict(float))
            all_outflows = defaultdict(lambda: defaultdict(float))

            for chain_dict in io_dicts['i']:
                if chain_dict != 'factory inflows':
                    chain_inflow_df = pan.DataFrame(io_dicts['i'][chain_dict])
                    df_list.append(chain_inflow_df)
                    sheet_list.append(chain_dict+" inflows")

                    chain_outflow_df = pan.DataFrame(io_dicts['o'][chain_dict])
                    df_list.append(chain_outflow_df)
                    sheet_list.append(chain_dict+" outflows")

                for process_dict in io_dicts['i'][chain_dict]:
                    if 'total' not in process_dict:
                        for substance, qty in io_dicts['i'][chain_dict][process_dict].items():
                            all_inflows[process_dict][substance] = qty
                        for substance, qty in io_dicts['o'][chain_dict][process_dict].items():
                            all_outflows[process_dict][substance] = qty

            all_outflows_df = pan.DataFrame(all_outflows)
            df_list.insert(1,all_outflows_df)
            sheet_list.insert(1, "unit outflow matrix")

            print(all_inflows)
            all_inflows_df = pan.DataFrame(all_inflows)
            print(all_inflows_df)
            df_list.insert(1, all_inflows_df)
            sheet_list.insert(1, "unit inflow matrix")

            iof.write_to_excel(df_list, sheet_list=sheet_list, 
                               filedir=dat.outdir, filename=filename)

        
        return io_dicts['i'], io_dicts['o']


    def diagram(self):
        """ Outputs a diagram of the factory flows to file.
        """

        if not self.chain_dict:
            self.initalize_factory()

        factory_diagram = Digraph(name="factory")
        factory_diagram.attr('node', shape='box', color='black')
        factory_diagrams = dict()
        io_diagram = Digraph(name=self.name, directory='outputFiles/pfd/factories', format='png',)
        io_diagram.attr('node', shape='box', color='white')
        

        # gets product chains
        for c in self.chain_dict:
            diagram_dict = dict(diagram=self.chain_dict[c]['chain'].diagram(
                                return_diagram=True, view_diagram=False),
                                process_list=self.chain_dict[c]['chain'].process_list, 
                                name=self.chain_dict[c]['name'], connect=[])
            if diagram_dict['name'] == self.main_chain:
                diagram_dict['diagram'].attr(rank='min')
            factory_diagrams[self.chain_dict[c]['name']] = diagram_dict

        # connects chains on factory intermediate products
        for i, c in self.connections_df.iterrows():
            product = c[dat.connect_product]
            origin_chain = c[dat.origin_chain]
            o_io = iof.fl(c[dat.origin_io])
            d_io = iof.fl(c[dat.dest_io])
            if d_io == 'i':
                dest_chain = c[dat.dest_chain]+factory_diagrams[c[dat.dest_chain]]['process_list'][0]['process'].name
            elif d_io == 'o':
                dest_chain = c[dat.dest_chain]+factory_diagrams[c[dat.dest_chain]]['process_list'][-1]['process'].name

            
            if c[dat.origin_process] == dat.connect_all:
                origin_list = [c[dat.origin_chain]+p['process'].name for 
                p in factory_diagrams[origin_chain]['process_list']]
            else:
                origin_list = [c[dat.origin_chain]+c[dat.origin_process]]

            for origin in origin_list:
                if d_io == 'i':
                    factory_diagram.edge(origin, dest_chain, label=product)
                    
                elif d_io == 'o':
                    factory_diagram.edge(dest_chain, origin, label=product)
                

        # add inflows and outflows
        for d in factory_diagrams:
            chain = factory_diagrams[d]['name']
            diagram = factory_diagrams[d]['diagram']
            process_list = factory_diagrams[d]['process_list']
            for i, unit in enumerate(process_list):
                process = unit['process'].name
                inflows = '\n'.join(unit['process'].inflows)
                outflows = '\n'.join(unit['process'].outflows)

                for dummy_index, c in self.connections_df.iterrows():
                    if chain == c[dat.origin_chain]:
                        if process == c[dat.origin_process] or c[dat.origin_process] == dat.connect_all:
                            if iof.fl(c[dat.origin_io]) == 'i':
                                inflows = inflows.replace(c[dat.connect_product], '')
                            if iof.fl(c[dat.origin_io]) == 'o':
                                outflows = outflows.replace(c[dat.connect_product], '')
                        
                    if chain == c[dat.dest_chain]:
                        if iof.fl(c[dat.dest_io]) == 'i' and unit == process_list[0]:
                            inflows = inflows.replace(c[dat.connect_product], '')
                        if iof.fl(c[dat.dest_io]) == 'o' and unit == process_list[-1]:
                            outflows = outflows.replace(c[dat.connect_product], '')

                if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')

                if i == 0:
                    if inflows and not inflows.isspace():
                        io_diagram.node(chain+process+inflows, label=inflows)
                        factory_diagram.edge(chain+process+inflows, chain+process, color='black')

                    if len(process_list) == 1:
                        if outflows and not outflows.isspace():
                            io_diagram.node(chain+process+outflows, label=outflows)
                            factory_diagram.edge(chain+process, chain+process+outflows)

                    elif outflows != unit['o']:
                        outflows = outflows.replace(unit['o'], '')
                        if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                        if outflows and not outflows.isspace():
                            io_diagram.node(chain+process+outflows, label=outflows)
                            factory_diagram.edge(chain+process, chain+process+outflows)


                elif i < len(process_list) - 1:
                    if inflows != unit['i']:
                        inflows = inflows.replace(unit['i'], '')
                        if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                        if inflows and not inflows.isspace():
                            io_diagram.node(chain+process+inflows, label=inflows)
                            factory_diagram.edge(chain+process+inflows, chain+process)

                    if outflows != unit['o']:
                        outflows = outflows.replace(unit['o'], '')
                        if '\n\n' in outflows: outflows = outflows.replace('\n\n', '\n')
                        if outflows and not outflows.isspace():
                            io_diagram.node(chain+process+outflows, label=outflows)
                            factory_diagram.edge(chain+process, chain+process+outflows)

                else:
                    if inflows != unit['i']:
                        inflows = inflows.replace(unit['i'], '')
                        if '\n\n' in inflows: inflows = inflows.replace('\n\n', '\n')
                        if inflows and not inflows.isspace():
                            io_diagram.node(chain+process+inflows, label=inflows)
                            factory_diagram.edge(chain+process+inflows, chain+process)
                    
                    if outflows and not outflows.isspace():
                        io_diagram.node(chain+process+outflows, label=outflows)
                        factory_diagram.edge(chain+process, chain+process+outflows)


        i = 0
        for diagram in factory_diagrams:
            factory_diagrams[diagram]['diagram'].attr('graph', name='cluster'+str(i))
            factory_diagram.subgraph(factory_diagrams[diagram]['diagram'])
        i += 1

        io_diagram.subgraph(factory_diagram)

        io_diagram.engine = 'circo'
        
        io_diagram.view()

            


# class Industry:
#     """
#     Industries are made up of one or more factories, and are balanced on one or more
#     factory products. Factories within an industry can run with different scenario
#     data. Industries can change over time.
#     """

#     def __init__(self, industry_data, name='Industry'):

#     def run_scenarios(self, scenario_list=[default_scenario]):

#     def evolve(self, start_scenarios, end_scenarios):
