"""TESTING FUNCTIONS
"""

from datetime import datetime
from collections import defaultdict
import pandas as pan

import blackblox.dataconfig as dat

# pause_between_tests = False

# for all tests
write_to_console = True
# dat.outdir = f'output/test_{datetime.now().strftime("%b%d")}/{datetime.now().strftime("%H%M")}'

# for chain, factory, and industry tests
view_diagrams = False
save_diagrams = False

# for factory and industry tests
write_to_xls = True

# for multi-scenario factory tests
individual_xls = True


###############################################################################
# SPECIFY TEST DATA
###############################################################################

qty = 1.0


#-------------------------------------------------------------------------------
# UNIT PROCESSES
#-------------------------------------------------------------------------------

scenario = 'default'

# PRODUCT TO BE TESTED - in run scenarios
scenario_product = False
scenario_unit = False
scenario_io = False


# compare_industry_name = 'EUROFER'
# compare_steps = [1990, 2010, 2030, 2050]
# compare_step_sheets = ['1990', '2010', '2030', '2050']
# compare_outflows = ['CO2__emitted', 'steel']
# compare_inflows = False

#  END OF USER INPUT SECTION  ==================================================
# ==============================================================================

import pandas as pan
import blackblox.io_functions as iof
import blackblox.unitprocess as uni
import blackblox.processchain as cha
import blackblox.factory as fac
import blackblox.industry as ind


#------------------------------------------------------------------------------
# UNIT TESTS

def test_units(unit_list, 
               qty=qty, 
               scenario=dat.default_scenario, 
               write_to_console=write_to_console):

    for unit_id in unit_list:
        unit = uni.UnitProcess(unit_id)

        print(str.upper(unit.name))
        print("\nmass inflows:", ', '.join(unit.mass_inflows))
        print("mass outflows:", ', '.join(unit.mass_outflows))
        print("\nenergy inflows:", ', '.join(unit.energy_inflows))
        print("energy outflows:", ', '.join(unit.energy_outflows))
        u_in, u_out = unit.balance(qty, scenario=scenario)

        if write_to_console is True:
            print(f"using {scenario} values:")
            flows = iof.make_df(dict(inflows=u_in, outflows=u_out))
            flows = iof.mass_energy_df(flows)
            print(flows)


#------------------------------------------------------------------------------
# CHAIN TESTS

def test_chains(chain_dict, 
                qty=qty, 
                scenario=scenario, 
                write_to_console=write_to_console, 
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams):
                
    for c in chain_dict:
        chain = cha.ProductChain(**chain_dict[c])
        print(f"\n{str.upper(chain.name)} chain")

        if view_diagrams is True or save_diagrams is True:
            chain.diagram(view=view_diagrams, save=save_diagrams)
        
        print(chain.process_dict)

        chain_inflows, chain_outflows, dummy_int_flows, int_rows = chain.balance(qty, scenario=scenario)

        if write_to_console is True:
            chain_inflows = iof.make_df(chain_inflows)
            chain_inflows = iof.mass_energy_df(chain_inflows)
            chain_outflows = iof.make_df(chain_outflows)
            chain_outflows = iof.mass_energy_df(chain_outflows)

            print(f'\nusing {scenario} values')
            print("\ninflows:\n", chain_inflows)
            print("\noutflows:\n", chain_outflows)

            print("\nintermediate flows:")
            for row in int_rows:
                print(row)


#------------------------------------------------------------------------------
# FACTORY TESTS


def build_factories(factory_dict):
    built_factories = dict()

    for f in factory_dict:
        factory = fac.Factory(**factory_dict[f])
        built_factories[f] = factory

        if view_diagrams is True or save_diagrams is True:
            factory.diagram(view=view_diagrams, save=save_diagrams)

    print("Factories successfully built:")
    for factory in built_factories:
        print(factory)

    return built_factories


def test_factories(factory_dict,
                qty=qty, 
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=False,
                upstream_outflows=False, 
                upstream_inflows=False,
                downstream_outflows=False,
                downstream_inflows=False,
                aggregate_flows=False,
                net_flows=False):

    
    built_factories = build_factories(factory_dict)
        
    print(f'\nbalancing factories on {qty} of main product... \n')
    for f in factory_dict:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory")
        
        f_dict = factory.balance(product_qty = qty, 
                                            scenario=factory_dict[f]['scenario'], 
                                            write_to_xls=write_to_xls, 
                                            outdir=outdir, 
                                            upstream_outflows=upstream_outflows, 
                                            upstream_inflows=upstream_inflows,
                                            downstream_outflows=downstream_outflows,
                                            downstream_inflows=downstream_inflows,
                                            aggregate_flows=aggregate_flows,
                                            net_flows=net_flows)

        if save_diagrams is True or view_diagrams is True:
            factory.diagram(outdir=f'{factory.outdir}/pfd', 
                            view=view_diagrams, 
                            save=save_diagrams)

        if write_to_console is True:
            print(f"\nusing {scenario} values and {qty} of {factory.main_product}:")
            totals = {'factory inflows': inflows, 'facto    ry outflows': outflows}
            totals = pan.DataFrame(f_dict[totals_in])
            totals = iof.mass_energy_df(totals)
            print(f"\n{factory.name} total inflows and outflows")
            print(totals)

        if write_to_xls is True:
            print(f"\n FACTORY: Full results available in {outdir} directory.")


def test_factory_scenarios(factory_dict,
                            scenario_factories, 
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            upstream_outflows=False, 
                            upstream_inflows=False,
                            downstream_outflows=False,
                            downstream_inflows=False,
                            aggregate_flows=False,
                            net_flows=False,
                            scenario_list=[dat.default_scenario], 
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            individual_xls=True,
                            view_diagrams=False,
                            save_diagrams=False,
                            outdir=dat.outdir,
                            filename='multifac_multiscenario',
                            productname='product'):

    print(f'\ncomparing factory outputs for {scenario_list}. for {qty} of product... \n')
    
    built_factories = build_factories(factory_dict)

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
                                                  write_to_xls=True,
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

        print(f"\n FACTORY (multi-scenario): Full results available in {outdir} directory.")
        first = False

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


# def test_factory_sensitivity(factory_dict,
#                             scenario_factories, 
#                             scenario,
#                             chain_name, 
#                             unit_name, 
#                             variable, 
#                             variable_options,
#                             fixed_vars=False,
#                             scenario_product=False,
#                             scenario_unit=False,
#                             scenario_io=False,
#                             qty=qty, 
#                             upstream_outflows=False, 
#                             upstream_inflows=False,
#                             downstream_outflows=False,
#                             downstream_inflows=False,
#                             aggregate_flows=False,
#                             write_to_console=write_to_console, 
#                             write_to_xls=write_to_xls,
#                             view_diagrams=view_diagrams,
#                             save_diagrams=save_diagrams,
#                             outdir=dat.outdir):

#     print(f'\ncomparing factory outputs for {scenario} for {variable} in {unit_name}. for {qty} of product... \n')
    
#     built_factories = build_factories(factory_dict)
#     sensitivity_dict = iof.nested_dicts(4) #dict[factory][io][scenario][flow] = qty
#     total_agg_in = False
#     total_agg_out = False

#     for f in scenario_factories:
#         factory = built_factories[f]
#         print(f"\n{str.upper(factory.name)} factory - sensitivity")

#         inflows, outflows, agg_in, agg_out, net_df = factory.run_sensitivity(product_qty=qty, 
#                                                     scenario=scenario, 
#                                                     chain_name=chain_name, 
#                                                     unit_name=unit_name, 
#                                                     variable=variable, 
#                                                     variable_options=variable_options,
#                                                     fixed_vars=fixed_vars,
#                                                     product=scenario_product, 
#                                                     product_unit=scenario_unit, 
#                                                     product_io=scenario_io,
#                                                     upstream_outflows=upstream_outflows, 
#                                                     upstream_inflows=upstream_inflows,                                     
#                                                     downstream_outflows=downstream_outflows,
#                                                     downstream_inflows=downstream_inflows,
#                                                     aggregate_flows=aggregate_flows,
#                                                     net_flows=net_flows,
#                                                     write_to_xls=individual_xls,
#                                                     outdir=outdir)


#         # sensitivity_dict[f"{f}_{scenario}"] = aggregate_dict

#         # inflow_dict = iof.nested_dicts(3)
#         # outflow_dict = iof.nested_dicts(3)
#         # for f in sensitivity_dict:
#         #     for scen in sensitivity_dict[f]['i']:
#         #         scen_short = scen.lstrip(f"{scenario}_")
#         #         scen_short = scen_short.lstrip(f"{unit_name}-")
#         #         scen_short = scen_short.lstrip(f"{variable}_")
#         #         for flow in sensitivity_dict[f]['i'][scen]:
#         #             inflow_dict[flow][scen_short][f] = sensitivity_dict[f]['i'][scen][flow]

#         #     for scen in sensitivity_dict[f]['o']:
#         #         scen_short = scen.lstrip(f"{scenario}_")
#         #         scen_short = scen_short.lstrip(f"{unit_name}-")
#         #         scen_short = scen_short.lstrip(f"{variable}_")
#         #         for flow in sensitivity_dict[f]['o'][scen]:
#         #             outflow_dict[flow][scen_short][f] = sensitivity_dict[f]['o'][scen][flow]

#         if total_agg_in = False:
#             total_agg_in = defaultdict()
#             for flow in  agg_in.index():
#                 total_agg_in[flow] = pan.DataFrame(columns=factory.name)

            
#         agg_in_dict[f"{f}_{scenario}"] = agg_in
#         agg_out_dict[f"{f}_{scenario}"] = agg_out
#         net_dict[f"{f}_{scenario}"] = net_df

#         for factory in agg_in_dict:
#             for col in agg_in_dict[f].columns():
#                 scen_short = scen.lstrip(f"{scenario}_")
#                 scen_short = scen_short.lstrip(f"{unit_name}-")
#                 scen_short = scen_short.lstrip(f"{variable}_")
#                 col = col.rename("scen_short")

#         if write_to_console is True:
#             print(f"\n{factory.name} inflows")
#             print(inflows)

#             print(f"\n{factory.name} outflows")
#             print(outflows)

#         print(f"\n FACTORY (sensitivity): Full results available in {outdir} directory.")
    



    # meta_df = iof.metadata_df(user=dat.user_data, 
    #                             name=f"{unit_name} {variable} sens", 
    #                             level="Factory", 
    #                             scenario=scenario, 
    #                             product='default',
    #                             product_qty=qty)

    # dfs = [meta_df]
    # sheets = ["meta"]

    # for flow in inflow_dict:
    #     df = iof.make_df(inflow_dict[flow])
    #     dfs.append(df)
    #     sheets.append(f"IN {flow}")

    # for flow in outflow_dict:
    #     df = iof.make_df(outflow_dict[flow])
    #     dfs.append(df)
    #     sheets.append(f"OUT {flow}")

    # iof.write_to_xls(df_or_df_list=dfs,
    #                     sheet_list=sheets, 
    #                     filedir=outdir, 
    #                     filename=f'{unit_name}_{variable}_sens{datetime.now().strftime("%Y-%m-%d_%H%M")}')

    # return inflow_dict, outflow_dict


#------------------------------------------------------------------------------
# INDUSTRY TEST


