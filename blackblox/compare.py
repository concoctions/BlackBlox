"""Functions to compare multiple ProductChains or Factories.
"""

from datetime import datetime
from collections import defaultdict
import pandas as pan

from blackblox.bb_log import get_logger
import blackblox.dataconfig as dat
import blackblox.io_functions as iof
import blackblox.unitprocess as uni
import blackblox.processchain as cha
import blackblox.factory as fac
import blackblox.industry as ind

logger = get_logger("Compare")


def multiple_units(unit_id_list, 
                   qty=1.0, 
                   scenario=dat.default_scenario, 
                   write_to_console=True):

    for unit_id in unit_id_list:
        unit = uni.UnitProcess(unit_id)
        unit.balance(qty, scenario=scenario, write_to_console=write_to_console)



#------------------------------------------------------------------------------
# CHAIN TESTS

dummy_chain_dict = {
                'chain1': dict(chain_data='filepath', 
                                    name='chain name', 
                                    xls_sheet='chain sheet',
                                    scenario='scenario'),
                'chain2': dict(chain_data='filepath', 
                                    name='chain name', 
                                    xls_sheet='chain sheet',
                                    scenario='scenario'),
}

def multiple_chains(chain_dict, 
                qty=1.0, 
                scenario=dat.default_scenario, 
                write_to_console=True,
                write_to_xls=False, 
                outdir=False, 
                view_diagrams=False,
                save_diagrams=True):
                
    for c in chain_dict:
        chain = cha.ProductChain(**chain_dict[c])
        print(f"\n{str.upper(chain.name)} chain")

        if view_diagrams is True or save_diagrams is True:
            chain.diagram(view=view_diagrams, save=save_diagrams, outdir=outdir)
        
        print(chain.process_dict)

        chain.balance(qty, 
                      scenario=scenario, 
                      write_to_console=write-to_console, 
                      write_to_xls=write_to_xls,
                      outdir=outdir)



#------------------------------------------------------------------------------
# FACTORY TESTS



def test_factories(factory_dict,
                qty=1.0, 
                write_to_console=False, 
                write_to_xls=True,
                view_diagrams=False,
                save_diagrams=True,
                outdir=False,
                upstream_outflows=False, 
                upstream_inflows=False,
                downstream_outflows=False,
                downstream_inflows=False,
                aggregate_flows=False,
                prebuilt=False):


    built_factories = dict()

    for f in factory_dict:
        factory = fac.Factory(**factory_dict[f])
        built_factories[f] = factory

    logger.debug(f"Factories successfully built: {[f for f in built_factories]}")
        
    print(f'\nbalancing factories on {qty} of main product... \n')
    for f in factory_dict:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory")
        
        inflows, outflows = factory.balance(product_qty = qty, 
                                            scenario=factory_dict[f]['scenario'], 
                                            write_to_xls=write_to_xls, 
                                            outdir=outdir, 
                                            upstream_outflows=upstream_outflows, 
                                            upstream_inflows=upstream_inflows,
                                            downstream_outflows=downstream_outflows,
                                            downstream_inflows=downstream_inflows,
                                            aggregate_flows=aggregate_flows)

        if save_diagrams is True or view_diagrams is True:
            factory.diagram(outdir=outdir, 
                            view=view_diagrams, 
                            save=save_diagrams)

        if write_to_console is True:
            print(f"\nusing {scenario} values and {qty} of {factory.main_product}:")
            totals = {'factory inflows': inflows, 'facto    ry outflows': outflows}
            totals = pan.DataFrame(totals)
            totals = iof.mass_energy_df(totals)
            print(f"\n{factory.name} total inflows and outflows")
            print(totals)

        if write_to_xls is True:
            print(f"\n FACTORY: Full results available in {dat.outdir} directory.")


def test_factory_scenarios(factory_dict,
                            scenario_factories, 
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=1.0, 
                            upstream_outflows=False, 
                            upstream_inflows=False,
                            downstream_outflows=False,
                            downstream_inflows=False,
                            aggregate_flows=False,
                            net_flows=False,
                            scenario_list=[dat.default_scenario], 
                            write_to_console=False, 
                            write_to_xls=True,
                            individual_xls=True,
                            factory_scenario_xls=True,
                            view_diagrams=False,
                            save_diagrams=True,
                            outdir=False,
                            filename='multiscenario',
                            productname='product'):

    print(f'\ncomparing factory outputs for {scenario_list}. for {qty} of product... \n')
    
    built_factories = dict()

    for f in factory_dict:
        factory = fac.Factory(**factory_dict[f])
        built_factories[f] = factory

    first = True
    for f in scenario_factories:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory - multiscenario")

        inflows, outflows, agg_inflows, agg_outflows, net_df = factory.run_scenarios(scenario_list=scenario_list, 
                                                  product_qty=qty, 
                                                  product=scenario_product, 
                                                  product_unit=scenario_unit, 
                                                  product_io=scenario_io,
                                                  upstream_outflows=upstream_outflows, 
                                                  upstream_inflows=upstream_inflows,
                                                  downstream_outflows=downstream_outflows,
                                                  downstream_inflows=downstream_inflows,
                                                  aggregate_flows=aggregate_flows,
                                                  net_flows=net_flows,
                                                  write_to_xls=factory_scenario_xls,
                                                  factory_xls=individual_xls,
                                                  outdir=outdir)

        if write_to_console is True:
            print(f"\n{factory.name} inflows")
            print(inflows)

            print(f"\n{factory.name} outflows")
            print(outflows)

        if save_diagrams is True or view_diagrams is True:
            factory.diagram(outdir=f'{outdir}/pfd', 
                            view=view_diagrams, 
                            save=save_diagrams)

        inflows = inflows.rename(columns=lambda x: f+"_"+x)   
        outflows = outflows.rename(columns=lambda x: f+"_"+x)
        agg_inflows = agg_inflows.rename(columns=lambda x: f+"_"+x)
        agg_outflows = agg_outflows.rename(columns=lambda x: f+"_"+x)
        net_df = net_df.rename(columns=lambda x: f+"_"+x)

        if first is True:
            all_inflows = inflows.copy()
            all_outflows = outflows.copy()
            all_agg_inflows = agg_inflows.copy()
            all_agg_outflows = agg_outflows.copy()
            all_net_flows = net_df.copy()
        else:
            all_inflows = pan.concat([all_inflows, inflows], ignore_index=False, sort=False, axis=1)
            all_outflows = pan.concat([all_outflows, outflows], ignore_index=False, sort=False, axis=1)

            all_agg_inflows = pan.concat([all_agg_inflows, agg_inflows], ignore_index=False, sort=False, axis=1)
            all_agg_outflows = pan.concat([all_agg_outflows, agg_outflows], ignore_index=False, sort=False, axis=1)

            all_net_flows = pan.concat([all_net_flows, net_df], ignore_index=False, sort=False, axis=1)

        
        first = False

    if write_to_xls is True:
        meta_df = iof.metadata_df(user=dat.user_data, 
                                name=filename, 
                                level="Multi Factory", 
                                scenario=" ,".join(scenario_list), 
                                product=productname,
                                product_qty=qty)

        dfs = [meta_df, all_inflows, all_outflows, all_agg_inflows.T, all_agg_outflows.T, all_net_flows.T]
        sheets = ["meta", "inflows", "outflows", "agg inflows", "agg outflows", "net flows"]

        iof.write_to_xls(df_or_df_list=dfs,
                            sheet_list=sheets, 
                            filedir=outdir, 
                            filename=f'{filename}_{datetime.now().strftime("%Y-%m-%d_%H%M")}')

        print(f"\n FACTORY (multi-scenario): Full results available in {outdir} directory.")

def test_factory_sensitivity(factory_dict,
                            scenario_factories, 
                            scenario,
                            chain_name, 
                            unit_name, 
                            variable, 
                            variable_options,
                            fixed_vars=False,
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            upstream_outflows=False, 
                            upstream_inflows=False,
                            downstream_outflows=False,
                            downstream_inflows=False,
                            aggregate_flows=False,
                            write_to_console=False, 
                            write_to_xls=True,
                            view_diagrams=False,
                            save_diagrams=True,
                            outdir=False):

    print(f'\ncomparing factory outputs for {scenario} for {variable} in {unit_name}. for {qty} of product... \n')
    
    built_factories = build_factories(factory_dict)
    sensitivity_dict = iof.nested_dicts(4) #dict[factory][io][scenario][flow] = qty

    for f in scenario_factories:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory - sensitivity")

        inflows, outflows, aggregate_dict = factory.run_sensitivity(product_qty=qty, 
                                                    scenario=scenario, 
                                                    chain_name=chain_name, 
                                                    unit_name=unit_name, 
                                                    variable=variable, 
                                                    variable_options=variable_options,
                                                    fixed_vars=fixed_vars,
                                                    product=scenario_product, 
                                                    product_unit=scenario_unit, 
                                                    product_io=scenario_io,
                                                    upstream_outflows=upstream_outflows, 
                                                    upstream_inflows=upstream_inflows,                                     
                                                    downstream_outflows=downstream_outflows,
                                                    downstream_inflows=downstream_inflows,
                                                    aggregate_flows=aggregate_flows,
                                                    write_to_xls=individual_xls,
                                                    outdir=outdir)

        sensitivity_dict[f"{f}_{scenario}"] = aggregate_dict

        if write_to_console is True:
            print(f"\n{factory.name} inflows")
            print(inflows)

            print(f"\n{factory.name} outflows")
            print(outflows)

        print(f"\n FACTORY (sensitivity): Full results available in {outdir} directory.")
    
    inflow_dict = iof.nested_dicts(3)
    outflow_dict = iof.nested_dicts(3)
    for f in sensitivity_dict:
        for scen in sensitivity_dict[f]['i']:
            scen_short = scen.lstrip(f"{scenario}_")
            scen_short = scen_short.lstrip(f"{unit_name}-")
            scen_short = scen_short.lstrip(f"{variable}_")
            for flow in sensitivity_dict[f]['i'][scen]:
                inflow_dict[flow][scen_short][f] = sensitivity_dict[f]['i'][scen][flow]

        for scen in sensitivity_dict[f]['o']:
            scen_short = scen.lstrip(f"{scenario}_")
            scen_short = scen_short.lstrip(f"{unit_name}-")
            scen_short = scen_short.lstrip(f"{variable}_")
            for flow in sensitivity_dict[f]['o'][scen]:
                outflow_dict[flow][scen_short][f] = sensitivity_dict[f]['o'][scen][flow]


    meta_df = iof.metadata_df(user=dat.user_data, 
                                name=f"{unit_name} {variable} sens", 
                                level="Factory", 
                                scenario=scenario, 
                                product='default',
                                product_qty=qty)

    dfs = [meta_df]
    sheets = ["meta"]

    for flow in inflow_dict:
        df = iof.make_df(inflow_dict[flow])
        dfs.append(df)
        sheets.append(f"IN {flow}")

    for flow in outflow_dict:
        df = iof.make_df(outflow_dict[flow])
        dfs.append(df)
        sheets.append(f"OUT {flow}")

    iof.write_to_xls(df_or_df_list=dfs,
                        sheet_list=sheets, 
                        filedir=outdir, 
                        filename=f'{unit_name}_{variable}_sens{datetime.now().strftime("%Y-%m-%d_%H%M")}')

    return inflow_dict, outflow_dict


# #------------------------------------------------------------------------------
# # INDUSTRY TEST


# def build_industries(industry_dict):
#     built_industries = dict()
#     for i in industry_dict:
#         industry = ind.Industry(**industry_dict[i])
#         built_industries[i] = industry

#     return built_industries

# def test_industries(industry_dict,
#                 industry_name='industry',
#                 scenario_id=scenario, 
#                 write_to_console=write_to_console, 
#                 upstream_outflows=False, 
#                 upstream_inflows=False,
#                 aggregate_flows=False,
#                 write_to_xls=write_to_xls,
#                 view_diagrams=view_diagrams,
#                 save_diagrams=save_diagrams,
#                 outdir=dat.outdir):

#     built_industries = build_industries(industry_dict)

#     ind_total = iof.nested_dicts(3) #[i_o][industry name][substance]
#     for i in industry_dict:
#         industry = built_industries[i]

#         ind_flows = industry.balance(outdir=outdir, **industry_dict[i], 
#                                     upstream_outflows=upstream_outflows, 
#                                     upstream_inflows=upstream_inflows, 
#                                     aggregate_flows=aggregate_flows)

#         ind_total['i'][i] = ind_flows['inflows']['industry totals']
#         ind_total['o'][i] = ind_flows['outflows']['industry totals']
    
#         filename = f'i_{industry_name}_comparison_{scenario_id}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'
        
#         infows_df = iof.make_df(ind_total['i'], drop_zero=True, metaprefix=None)
#         infows_df = iof.mass_energy_df(infows_df, aggregate_consumed=True)
#         outflows_df = iof.make_df(ind_total['o'], drop_zero=True, metaprefix=None)
#         outflows_df = iof.mass_energy_df(outflows_df, aggregate_consumed=True)

#         meta_df = iof.metadata_df(user=dat.user_data, name=f'{industry_name}_comparison', 
#                         level="Industry", scenario="n/a", product="n/a",
#                         product_qty="n/a", energy_flows=dat.energy_flows)

#         df_list = [meta_df, infows_df, outflows_df]
#         sheet_list = ["meta", "inflows", "outflows"]
        
#         iof.write_to_xls(df_list, sheet_list=sheet_list, filedir=dat.outdir, filename=filename)
    
#         print(f"\n STATIC INDUSTRY COMPARISON - Full results available in {dat.outdir} directory.")


# def test_industry_evolve(
#                 industry_dict,
#                 qty, 
#                 compare_steps,
#                 compare_step_sheets,
#                 compare_industry_name='Industry',
#                 compare_evolved_industres=True,
#                 compare_outflows=False,
#                 compare_inflows=False,
#                 write_to_console=write_to_console, 
#                 write_to_xls=write_to_xls,
#                 view_diagrams=view_diagrams,
#                 save_diagrams=save_diagrams,
#                 outdir=dat.outdir):

#     built_industries = build_industries(industry_dict)

#     ind_annual = iof.nested_dicts(4) #[i_o][industry name][substance][time step]
#     ind_cumulative = iof.nested_dicts(3) #[i_o][industry name][substance]
#     for i in industry_dict:
#         industry = built_industries[i]
#         if compare_evolved_industres is True and compare_steps is not False:
#             industry_dict[i]['steps'] = compare_steps
#         if compare_evolved_industres is True and compare_step_sheets is not False:
#             industry_dict[i]['step sheets'] = compare_step_sheets
#         annual, cumulative = industry.evolve_multistep(outdir=outdir, **industry_dict[i])

#         ind_annual['i'][i] = annual['inflows']['industry totals']
#         ind_annual['o'][i] = annual['outflows']['industry totals']

#         ind_cumulative['i'][i] = cumulative['inflows']['industry totals']
#         ind_cumulative['o'][i] = cumulative['outflows']['industry totals']
    
#     if compare_evolved_industres is True and compare_steps is not False:

#         filename = (f'i_{compare_industry_name}_comparison_{compare_steps[0]}-{compare_steps[-1]}'
#                     f'_{datetime.now().strftime("%Y-%m-%d_%H%M")}')

#         cumulative_infows_df = iof.make_df(ind_cumulative['i'], drop_zero=True, metaprefix=None)
#         cumulative_infows_df = iof.mass_energy_df(cumulative_infows_df, aggregate_consumed=True)
#         cumulative_outflows_df = iof.make_df(ind_cumulative['o'], drop_zero=True, metaprefix=None)
#         cumulative_outflows_df = iof.mass_energy_df(cumulative_outflows_df, aggregate_consumed=True)

#         meta_df = iof.metadata_df(user=dat.user_data, name=f'{compare_industry_name}_comparison', 
#                         level="Industry", scenario="n/a", product="n/a",
#                         product_qty="n/a", energy_flows=dat.energy_flows)

#         df_list = [meta_df, cumulative_infows_df, cumulative_outflows_df]
#         sheet_list = ["meta", "inflows (cumulative)", "outflows (cumulative)"]

#         df_dict = iof.nested_dicts(2)

#         for flow in ind_annual:
#             for factory in ind_annual[flow]:
#                 df = iof.make_df(ind_annual[flow][factory], drop_zero=False, sort=True, metaprefix=None)
#                 sheet_name = f'{factory} {flow}'
#                 df_dict[flow[0]][factory] = df
#                 df_list.append(df)
#                 sheet_list.append(sheet_name)
        
#         iof.write_to_xls(df_list, sheet_list=sheet_list, filedir=dat.outdir, filename=filename)

#         if type(compare_outflows) is list:
#             for flow in compare_outflows:
#                 iof.plot_annual_flows(df_dict['o'], flow, dat.outdir, file_id=f"_{compare_industry_name}-comparison")

#         if type(compare_inflows) is list:
#             for flow in compare_outflows:
#                 iof.plot_annual_flows(df_dict['i'], flow, dat.outdir, file_id=f"_{compare_industry_name}-comparison")

    
#         print(f"\n INDUSTRY COMPARISON - Full results available in {dat.outdir} directory.")



# def main():
#     pass

# if __name__ == "__main__":
#     main()