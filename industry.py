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
        self.factories_df = iof.make_df(factory_list_file, factory_list_sheet, index=None)
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

            f_chains_sheet = iof.check_for_col(self.factories_df, dat.f_chains_sheet, i)
            f_connections_sheet = iof.check_for_col(self.factories_df, dat.f_connections_sheet, i)

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
                force_scenario=None, write_to_xls=True, outdir=dat.outdir, 
                subfolder=True, foldertime=True, file_id='', diagrams=False):
        """Balances an industry using one scenario for each factory.
        """
        if self.factory_dict is None:
            self.initalize()

        if subfolder is True:
            subfolder = self.name

        outdir = iof.build_filedir(outdir, subfolder=subfolder,
                                        file_id_list=[file_id],
                                        time=foldertime)
            
        if products_data is None and products_sheet is None:
            raise Exception("Neither data file path nor data sheet provided")
        elif products_data is None:
            products_data = self.factory_file

        product_df = iof.make_df(products_data, sheet=products_sheet)
        f_production_dict = defaultdict(dict)

        fractions = defaultdict(float) 
        product_scenario = defaultdict(float)

        io_dicts=  iof.nested_dicts(3, float)

        for i, f in product_df.iterrows():
            product = f[dat.f_product]
            if iof.sl(i) in dat.all_factories: 
                if product not in dat.no_var:
                    fractions[product] = f[dat.f_product_qty] # industry-wide product total
                if isinstance(f[dat.f_scenario], str) and iof.sl(f[dat.f_scenario]) not in dat.no_var:
                    product_scenario[product]=f[dat.f_scenario] #scenario for all factories producing that product
            else:
                if product in fractions: # product qty should be decimal fraction of total
                    calc.check_qty(f[dat.f_product_qty], fraction=True)
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
            io_dicts['inflows'][f], io_dicts['outflows'][f] = factory.balance(**f_kwargs)

            if diagrams is not False:
                factory.diagram(outdir=outdir+'/pfd')

        totals_in = defaultdict(float)
        totals_out = defaultdict(float)

        for factory in io_dicts['inflows']:
            for substance, qty in io_dicts['inflows'][factory].items():
                totals_in[substance] += qty
            for substance, qty in io_dicts['outflows'][factory].items():
                totals_out[substance] += qty

        io_dicts['inflows']['industry totals'] = totals_in
        io_dicts['outflows']['industry totals'] = totals_out

        if write_to_xls is True:
            filename = f'i_{self.name}_{file_id}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'

            inflows_df = iof.make_df(io_dicts['inflows'], drop_zero=True)
            outflows_df = iof.make_df(io_dicts['outflows'], drop_zero=True)

            df_list = [inflows_df, outflows_df]
            sheet_list = [f'{self.name} inflows', f'{self.name} outflows']
            
            iof.write_to_excel(df_list, sheet_list=sheet_list, 
                               filedir=outdir, filename=filename)

        return io_dicts #io_dicts[flow type][factory][substance] = qty



    def run_scenarios(self, scenario_list, products_data=None, products_sheet=None, 
                write_to_xls=True, outdir=dat.outdir, file_id='', diagrams=False):
        """Balances the industry on a set of forced industry-wide scenarios
        """

        outdir = iof.build_filedir(outdir, subfolder=self.name,
                                    file_id_list=['multiScenario', file_id],
                                    time=True)

        for scenario in scenario_list:
            self.balance(products_data=products_data, 
                         products_sheet=products_sheet, 
                         force_scenario=scenario, 
                         write_to_xls=write_to_xls, 
                         outdir=f'{outdir}/{scenario}', 
                         file_id=f'{file_id}_{scenario}', 
                         diagrams=diagrams)



    def evolve(self, start_data=None, start_sheet=None, end_data=None, end_sheet=None,
                start_step=0, end_step=1,
                write_to_xls=True, outdir=dat.outdir, file_id='', diagrams=False):  
        """Calculates timestep and cumulative inflows and outflows of an industry
        using a specified starting scenario and end scenario
        """

        outdir = iof.build_filedir(outdir, subfolder=self.name,
                                    file_id_list=['evolve', start_step, end_step, file_id],
                                    time=True)

        kwargs = dict(write_to_xls=write_to_xls,
                      diagrams=diagrams,
                      file_id=file_id,
                      subfolder=None,
                      foldertime=False)

        start_io = self.balance(products_data=start_data, 
                                products_sheet=start_sheet, 
                                outdir=f'{outdir}/start_{start_step}',
                                **kwargs)

        end_io = self.balance(products_data=end_data, 
                              products_sheet=end_sheet, 
                              outdir=f'{outdir}/end_{end_step}',
                              **kwargs)

        #io_dicts in the form of:
        # io_dict['factory name' or 'industry totals']['inflows' or 'outflows']['substance'] = qty

        #harmonize start_io and end_io dict keys:

        to_harmonize = [(start_io, end_io), (end_io, start_io),]

        for pair in to_harmonize:
            for flow in pair[0]:
                for factory in pair[0][flow]:
                    for substance in pair[1][flow][factory]:
                        if substance not in pair[0][flow][factory]:
                            pair[0][flow][factory][substance] = 0


        stepcount = end_step - start_step
        slope_dict = iof.nested_dicts(3)
        

        for flow in end_io:
            for factory in end_io[flow]:
                for substance in end_io[flow][factory]:
                    end_qty = end_io[flow][factory][substance]
                    start_qty = start_io[flow][factory][substance]
                    slope = ((end_qty - start_qty)/stepcount)    # m = (y-b)/x
                    slope_dict[flow][factory][substance] = slope


        annual_flows = iof.nested_dicts(4)
        cumulative_dict = iof.nested_dicts(3)

        for i in range(stepcount+1):
            step = str(start_step + i)
            for flow in start_io:
                for factory in start_io[flow]:
                    for substance, qty in start_io[flow][factory].items():
                        slope = slope_dict[flow][factory][substance] 
                        step_qty = qty + (i * slope)  # y = mx + b
                        annual_flows[flow][factory][substance][step] = step_qty
                        cumulative_dict[flow][factory][substance] += step_qty

        if write_to_xls is True:

            filename = (f'i_{self.name}_{start_step}-{end_step}_{file_id}'
                        f'_{datetime.now().strftime("%Y-%m-%d_%H%M")}')

            cumulative_infows_df = iof.make_df(cumulative_dict['inflows'], drop_zero=True)
            cumulative_outflows_df = iof.make_df(cumulative_dict['outflows'], drop_zero=True)

            df_list = [cumulative_infows_df, cumulative_outflows_df]
            sheet_list = ["cumulative inflows", "cumulative outflows"]

            for flow in annual_flows:
                for factory in annual_flows[flow]:
                    df = iof.make_df(annual_flows[flow][factory], drop_zero=True)
                    sheet_name = f'{factory} {flow}'

                    if 'total' in factory:
                        df_list.insert(0, df)
                        sheet_list.insert(0,sheet_name)
                    else:
                        df_list.append(df)
                        sheet_list.append(sheet_name)
            
            iof.write_to_excel(df_list, sheet_list=sheet_list, 
                               filedir=outdir, filename=filename)

        return annual_flows, cumulative_dict

    
    
    def evolve_multistep(self, start_data, step_data, start_sheet=None, step_sheets=None):
        pass
