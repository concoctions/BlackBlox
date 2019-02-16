import pandas as pan
from collections import defaultdict
from graphviz import Digraph
from datetime import datetime

from bb_log import get_logger

import io_functions as iof
import dataconfig as dat
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

    def __init__(self, chain_list_file, connections_file=None, chain_list_sheet=None, 
                 connections_sheet=None, name="Factory"):
        self.name = name
        self.chains_file = chain_list_file
        self.chains_df = iof.make_df(chain_list_file, chain_list_sheet, index=None)
        if connections_file is None:
            self.connections_df = iof.make_df(chain_list_file, connections_sheet, index=None)
        else:
            self.connections_df = iof.make_df(connections_file, connections_sheet, index=None)
        self.main_chain = False
        self.main_product = False
        self.chain_dict = False

    def initalize(self):
        logger.debug(f"initializing factory for {self.name}")
        
        chain_dict = defaultdict(dict)

        for i, c in self.chains_df.iterrows():
            name = c[dat.chain_name] 
            if i == 0:
                self.main_chain = name
                self.main_product = c[dat.chain_product]
            
            chain_sheet = iof.check_for_col(self.chains_df, dat.chain_sheetname, i)

            if (dat.chain_filepath not in self.chains_df 
                or iof.clean_str(c[dat.chain_filepath]) in dat.same_xls):
                chain_file = self.chains_file
            else:
                chain_file = c[dat.chain_filepath]
                
            chain_dict[name] = dict(chain=cha.ProductChain(chain_file, 
                                    name=name, xls_sheet=chain_sheet), 
                                    name=name, 
                                    product=c[dat.chain_product], 
                                    i_o=iof.clean_str(c[dat.chain_io][0]))

        self.chain_dict = chain_dict

    def balance(self, main_product_qty, var_i=dat.default_scenario, write_to_xls=True, outdir=dat.outdir):
        if not self.chain_dict:
            self.initalize()

        logger.debug(f"balancing factory on {main_product_qty} of {self.chain_dict[self.main_chain]['product']}")

        io_dicts = {
            'i': iof.nested_dicts(3, float),
            'o': iof.nested_dicts(3, float)
            }

        intermediate_product_dict = defaultdict(float)
           

        m = self.chain_dict[self.main_chain]
        
        # balances main chain
        io_dicts['i'][m['name']], io_dicts['o'][m['name']] = m['chain'].balance(
            main_product_qty, product= m['product'], var_i=var_i)

        for dummy_index, c in self.connections_df.iterrows():    
            qty = False
            o_io = iof.clean_str(c[dat.origin_io][0])
            d_io = iof.clean_str(c[dat.dest_io][0])

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
                totals[io_dict][product] -= qty


        # OPTIONAL: writes to spreadsheet
        if write_to_xls is True:
            if outdir == dat.outdir:
                outdir = f'{dat.outdir}/{self.name}'
                
            filename = f'f_{self.name}_{var_i}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

            totals_dict = defaultdict(lambda: defaultdict(float))
            totals_dict['factory inflows'] = totals['i']
            totals_dict['factory outflows'] = totals['o']
            totalsDF = iof.make_df(totals_dict, drop_zero=True)

            df_list = [totalsDF]
            sheet_list = [f'{self.name} totals']

            all_inflows = defaultdict(lambda: defaultdict(float))
            all_outflows = defaultdict(lambda: defaultdict(float))

            for chain_dict in io_dicts['i']:
                chain_inflow_df = iof.make_df(io_dicts['i'][chain_dict], drop_zero=True)
                df_list.append(chain_inflow_df)
                sheet_list.append(chain_dict+" inflows")

                chain_outflow_df = iof.make_df(io_dicts['o'][chain_dict], drop_zero=True)
                df_list.append(chain_outflow_df)
                sheet_list.append(chain_dict+" outflows")

                for process_dict in io_dicts['i'][chain_dict]:
                    if 'total' not in process_dict:
                        for substance, qty in io_dicts['i'][chain_dict][process_dict].items():
                            all_inflows[process_dict][substance] = qty
                        for substance, qty in io_dicts['o'][chain_dict][process_dict].items():
                            all_outflows[process_dict][substance] = qty

            all_outflows_df = iof.make_df(all_outflows, drop_zero=True)
            df_list.insert(1,all_outflows_df)
            sheet_list.insert(1, "unit outflow matrix")

            all_inflows_df = iof.make_df(all_inflows, drop_zero=True)
            df_list.insert(1, all_inflows_df)
            sheet_list.insert(1, "unit inflow matrix")

            iof.write_to_excel(df_list, sheet_list=sheet_list, 
                               filedir=outdir, filename=filename)

        
        return totals['i'], totals['o']


    def diagram(self, outdir=dat.outdir, view=False):
        """ Outputs a diagram of the factory flows to file.
        """

        if outdir == dat.outdir:
            outdir = f'{outdir}/{self.name}/pfd'

        if not self.chain_dict:
            self.initalize()

        factory_diagram = Digraph(name="factory")
        factory_diagram.attr('node', shape='box', color='black')
        factory_diagrams = dict()
        io_diagram = Digraph(name=self.name, directory=outdir, format='png',)
        io_diagram.attr('node', shape='box', color='white')
        

        # gets product chains
        for c in self.chain_dict:
            d_kwargs = dict(return_diagram=True,
                            view_diagram=False,
                            outdir=f'{outdir}/{self.name}')
            diagram_dict = dict(diagram=self.chain_dict[c]['chain'].diagram(**d_kwargs),
                                process_list=self.chain_dict[c]['chain'].process_list, 
                                name=self.chain_dict[c]['name'], connect=[])
            if diagram_dict['name'] == self.main_chain:
                diagram_dict['diagram'].attr(rank='min')
            factory_diagrams[self.chain_dict[c]['name']] = diagram_dict

        # connects chains on factory intermediate products
        for i, c in self.connections_df.iterrows():
            product = c[dat.connect_product]
            origin_chain = c[dat.origin_chain]
            o_io = iof.clean_str(c[dat.origin_io][0])
            d_io = iof.clean_str(c[dat.dest_io][0])
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
                            if iof.clean_str(c[dat.origin_io][0]) == 'i':
                                inflows = inflows.replace(c[dat.connect_product], '')
                            if iof.clean_str(c[dat.origin_io][0]) == 'o':
                                outflows = outflows.replace(c[dat.connect_product], '')
                        
                    if chain == c[dat.dest_chain]:
                        if iof.clean_str(c[dat.dest_io][0]) == 'i' and unit == process_list[0]:
                            inflows = inflows.replace(c[dat.connect_product], '')
                        if iof.clean_str(c[dat.dest_io][0]) == 'o' and unit == process_list[-1]:
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
        
        if view is True:
            io_diagram.view()

        io_diagram.render()
        io_diagram.format = 'svg'
        io_diagram.render()