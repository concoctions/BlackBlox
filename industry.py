import pandas as pan
from collections import defaultdict
from graphviz import Digraph
from datetime import datetime

from bb_log import get_logger

import io_functions as iof
import dataconfig as dat
import factory as fac
import calculators as calc


logger = get_logger("Industry")

class Industry:
    """
    Industries are made up of one or more factories, and are balanced on one or more
    factory products. Factories within an industry can run with different scenario
    data. Industries can change over time.
    """

    def __init__(self, factory_list_file, factory_list_sheet=None, name='Industry', **kwargs):
        self.name = name
        self.factory_file = factory_list_file
        self.factories_df = iof.check_if_df(factory_list_file, factory_list_sheet, index=None)
        self.product_list = None
        self.factory_dict = None

    def initalize(self):
        """ generates the factory, chain, and process objects in the industry
        """
        logger.debug(f"initializing industry for {self.name}")

        factory_dict = defaultdict(dict)
        product_list = set()

        for i, f in self.factories_df.iterrows():
            name = f[dat.factory_name]
            if dat.factory_filepath in self.factories_df:
                f_chains_file = f[dat.factory_filepath]
                f_connections_file = f[dat.factory_filepath]
            else:
                f_chains_file = f[dat.f_chain_list_file]
                f_connections_file = f[dat.f_connections_file]

            f_chains_sheet = iof.check_sheet(self.factories_df, dat.f_chains_sheet, i)
            f_connections_sheet = iof.check_sheet(self.factories_df, dat.f_connections_sheet, i)

            f_kwargs = dict(chain_list_file=f_chains_file,
                            connections_file=f_connections_file, 
                            chain_list_sheet=f_chains_sheet, 
                            connections_sheet=f_connections_sheet, 
                            name=name)

            factory = fac.Factory(**f_kwargs)
            factory.initalize()

            factory_dict[name] = dict(factory=factory,
                                      product=factory.main_product,
                                      name=name)

            product_list.add(factory.main_product)

            self.factory_dict = factory_dict
            self.product_list = product_list
    
    def balance(self, products_data=None, products_sheet=None, 
                force_scenario=None, write_to_xls=False, outdir=dat.outdir, 
                file_id=None, diagrams=False):
        """Balances an industry using one scenario for each factory.
        """
        if self.factory_dict is None:
            self.initalize()

        if outdir == dat.outdir:
            outdir = f'{outdir}/{self.name}'
        
        if file_id is not None:
            outdir = f'{outdir}_{file_id}'

        outdir = outdir+datetime.now().strftime("%Y-%m-%d_%H%M")
            
        if products_data is None and products_sheet is None:
            raise Exception("Neither data file path nor data sheet provided")
        elif products_data is None:
            products_data = self.factory_file

        product_df = iof.check_if_df(products_data, sheet=products_sheet)
        f_production_dict = defaultdict(dict)

        fractions = defaultdict(float) 
        product_scenario = defaultdict(float)

        io_dicts=  iof.nested_dicts(3, float)

        for i, f in product_df.iterrows():
            product = f[dat.f_product]
            if iof.s_l(i) in dat.all_factories: 
                if product not in dat.no_var:
                    fractions[product] = f[dat.f_product_qty] # industry-wide product total
                if isinstance(f[dat.f_scenario], str) and iof.s_l(f[dat.f_scenario]) not in dat.no_var:
                    product_scenario[product]=f[dat.f_scenario] #scenario for all factories producing that product
            else:
                if product in fractions: # product qty should be decimal fraction of total
                    calc.CheckQty(f[dat.f_product_qty], fraction=True)
                    product_qty = f[dat.f_product_qty] * fractions[product]
                else:
                    product_qty = f[dat.f_product_qty]

                if force_scenario is not None:
                    scenario = force_scenario
                else:
                    if product in product_scenario:
                        scenario = product_scenario[product]
                    else:
                        scenario = f[dat.f_scenario]
                

                f_production_dict[i] = dict(main_product_qty=product_qty,
                                    var_i=scenario,
                                    write_to_xls=write_to_xls,
                                    outdir=f'{outdir}/factories')

        for f in f_production_dict:
            factory = self.factory_dict[f]['factory']
            f_kwargs = f_production_dict[f]
            io_dicts[f]['inflows'], io_dicts[f]['outflows'] = factory.balance(**f_kwargs)

            if diagrams is not False:
                factory.diagram(outdir=outdir+'/pfd')

        total_inflows = defaultdict(float)
        total_outflows = defaultdict(float)

        for factory in io_dicts:
            for substance, qty in io_dicts[factory]['inflows'].items():
                total_inflows[substance] += qty
            for substance, qty in io_dicts[factory]['outflows'].items():
                total_outflows[substance] += qty

        io_dicts['industry totals']['inflows'] = total_inflows
        io_dicts['industry totals']['outflows'] = total_outflows

        if write_to_xls is True:
            if file_id is None:
                filename = f'i_{self.name}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'
            else:
                filename = f'i_{self.name}_{file_id}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

            totals_dict = {'industry total inflows': io_dicts['industry totals']['inflows'],
                            'industry total outflows': io_dicts['industry totals']['outflows'] }
        
            totalsDF = pan.DataFrame(totals_dict)

            df_list = [totalsDF]
            sheet_list = [f'{self.name} totals']

            for f in io_dicts:
                if f is not 'industry totals':
                    df = pan.DataFrame(io_dicts[f])
                    df_list.append(df)
                    sheet_list.append(f)
            
            iof.write_to_excel(df_list, sheet_list=sheet_list, 
                               filedir=outdir, filename=filename)

        return io_dicts


    def run_scenarios(self, scenario_list, products_data=None, products_sheet=None, 
                write_to_xls=True, outdir=dat.outdir, file_id=None, diagrams=False):
        """Balances the industry on a set of forced industry-wide scenarios
        """
        if outdir == dat.outdir:
            outdir = f'{outdir}/{self.name}_multiScenario'

        if file_id is not None:
            outdir = f'{outdir}_{file_id}'

        outdir = f'{outdir}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

        for scenario in scenario_list:
            self.balance(products_data=products_data, 
                         products_sheet=products_sheet, 
                         force_scenario=scenario, 
                         write_to_xls=write_to_xls, 
                         outdir=f'{outdir}/{scenario}', 
                         file_id=f'{file_id}_{scenario}', 
                         diagrams=diagrams)


    def evolve_once(self, evolution_data, sheets=None):  
        """Balances the industry on a first 
        evolution_data (string or list of strings)
        sheets (string or list of strings)
        """
        pass
    
    def evolve(self, evolution_data, sheets=None):
        pass
