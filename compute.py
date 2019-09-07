"""TESTING FUNCTIONS
"""

import dataconfig as dat
from datetime import datetime
from collections import defaultdict


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
import io_functions as iof
import unitprocess as uni
import processchain as cha
import factory as fac
import industry as ind


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
        chain.build()
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
        factory.build()
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
                outdir=dat.outdir,
                upstream_outflows=False, 
                upstream_inflows=False,
                aggregate_flows=False,
                prebuilt=False):

    if prebuilt is not False:
        built_factories = prebuilt
    else:
        built_factories = build_factories(factory_dict)
        
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
                                            aggregate_flows=aggregate_flows,
                                            mass_energy=True, 
                                            energy_flows=dat.energy_flows,)

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
                            qty=qty, 
                            upstream_outflows=False, 
                            upstream_inflows=False,
                            aggregate_flows=False,
                            scenario_list=[dat.default_scenario], 
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=dat.outdir):

    print(f'\ncomparing factory outputs for {scenario_list}. for {qty} of product... \n')
    
    built_factories = build_factories(factory_dict)

    for f in scenario_factories:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory - multiscenario")

        inflows, outflows = factory.run_scenarios(scenario_list=scenario_list, 
                                                  product_qty=qty, 
                                                  product=scenario_product, 
                                                  product_unit=scenario_unit, 
                                                  product_io=scenario_io,
                                                  upstream_outflows=upstream_outflows, 
                                                  upstream_inflows=upstream_inflows,
                                                  aggregate_flows=aggregate_flows,
                                                  write_to_xls=individual_xls,
                                                  outdir=outdir)

        if write_to_console is True:
            print(f"\n{factory.name} inflows")
            print(inflows)

            print(f"\n{factory.name} outflows")
            print(outflows)

        if save_diagrams is True or view_diagrams is True:
            factory.diagram(outdir=outdir, 
                            view=view_diagrams, 
                            save=save_diagrams)
                            
        print(f"\n FACTORY (multi-scenario): Full results available in {outdir} directory.")


def test_factory_sensitivity(factory_dict,
                            scenario_factories, 
                            scenario,
                            chain_name, 
                            unit_name, 
                            variable, 
                            variable_options,
                            scenario_product=False,
                            scenario_unit=False,
                            scenario_io=False,
                            qty=qty, 
                            upstream_outflows=False, 
                            upstream_inflows=False,
                            aggregate_flows=False,
                            write_to_console=write_to_console, 
                            write_to_xls=write_to_xls,
                            view_diagrams=view_diagrams,
                            save_diagrams=save_diagrams,
                            outdir=dat.outdir):

    print(f'\ncomparing factory outputs for {scenario} for {variable} in {unit_name}. for {qty} of product... \n')
    
    built_factories = build_factories(factory_dict)

    for f in scenario_factories:
        factory = built_factories[f]
        print(f"\n{str.upper(factory.name)} factory - sensitivity")

        inflows, outflows = factory.run_sensitivity(product_qty=qty, 
                                                    base_scenario=scenario, 
                                                    chain_name=chain_name, 
                                                    unit_name=unit_name, 
                                                    variable=variable, 
                                                    variable_options=variable_options,
                                                    product=scenario_product, 
                                                    product_unit=scenario_unit, 
                                                    product_io=scenario_io,
                                                    upstream_outflows=upstream_outflows, 
                                                    upstream_inflows=upstream_inflows,
                                                    aggregate_flows=aggregate_flows,
                                                    write_to_xls=individual_xls,
                                                    outdir=outdir)

        if write_to_console is True:
            print(f"\n{factory.name} inflows")
            print(inflows)

            print(f"\n{factory.name} outflows")
            print(outflows)

        print(f"\n FACTORY (sensitivity): Full results available in {outdir} directory.")


#------------------------------------------------------------------------------
# INDUSTRY TEST


def build_industries(industry_dict):
    built_industries = dict()
    for i in industry_dict:
        industry = ind.Industry(**industry_dict[i])
        built_industries[i] = industry

    return built_industries

def test_industries(industry_dict,
                industry_name='industry',
                scenario_id=scenario, 
                write_to_console=write_to_console, 
                upstream_outflows=False, 
                upstream_inflows=False,
                aggregate_flows=False,
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=dat.outdir):

    built_industries = build_industries(industry_dict)

    ind_total = iof.nested_dicts(3) #[i_o][industry name][substance]
    for i in industry_dict:
        industry = built_industries[i]

        ind_flows = industry.balance(outdir=outdir, **industry_dict[i], 
                                    upstream_outflows=upstream_outflows, 
                                    upstream_inflows=upstream_inflows, 
                                    aggregate_flows=aggregate_flows)

        ind_total['i'][i] = ind_flows['inflows']['industry totals']
        ind_total['o'][i] = ind_flows['outflows']['industry totals']
    
        filename = f'i_{industry_name}_comparison_{scenario_id}_{datetime.now().strftime("%Y-%m-%d_%H%M")}'
        
        infows_df = iof.make_df(ind_total['i'], drop_zero=True, metaprefix=None)
        infows_df = iof.mass_energy_df(infows_df, aggregate_consumed=True)
        outflows_df = iof.make_df(ind_total['o'], drop_zero=True, metaprefix=None)
        outflows_df = iof.mass_energy_df(outflows_df, aggregate_consumed=True)

        meta_df = iof.metadata_df(user=dat.user_data, name=f'{industry_name}_comparison', 
                        level="Industry", scenario="n/a", product="n/a",
                        product_qty="n/a", energy_flows=dat.energy_flows)

        df_list = [meta_df, infows_df, outflows_df]
        sheet_list = ["meta", "inflows", "outflows"]
        
        iof.write_to_excel(df_list, sheet_list=sheet_list, filedir=dat.outdir, filename=filename)
    
        print(f"\n STATIC INDUSTRY COMPARISON - Full results available in {dat.outdir} directory.")


def test_industry_evolve(
                industry_dict,
                qty, 
                compare_steps,
                compare_step_sheets,
                compare_industry_name='Industry',
                compare_evolved_industres=True,
                compare_outflows=False,
                compare_inflows=False,
                write_to_console=write_to_console, 
                write_to_xls=write_to_xls,
                view_diagrams=view_diagrams,
                save_diagrams=save_diagrams,
                outdir=dat.outdir):

    built_industries = build_industries(industry_dict)

    ind_annual = iof.nested_dicts(4) #[i_o][industry name][substance][time step]
    ind_cumulative = iof.nested_dicts(3) #[i_o][industry name][substance]
    for i in industry_dict:
        industry = built_industries[i]
        if compare_evolved_industres is True and compare_steps is not False:
            industry_dict[i]['steps'] = compare_steps
        if compare_evolved_industres is True and compare_step_sheets is not False:
            industry_dict[i]['step sheets'] = compare_step_sheets
        annual, cumulative = industry.evolve_multistep(outdir=outdir, **industry_dict[i])

        ind_annual['i'][i] = annual['inflows']['industry totals']
        ind_annual['o'][i] = annual['outflows']['industry totals']

        ind_cumulative['i'][i] = cumulative['inflows']['industry totals']
        ind_cumulative['o'][i] = cumulative['outflows']['industry totals']
    
    if compare_evolved_industres is True and compare_steps is not False:

        filename = (f'i_{compare_industry_name}_comparison_{compare_steps[0]}-{compare_steps[-1]}'
                    f'_{datetime.now().strftime("%Y-%m-%d_%H%M")}')

        cumulative_infows_df = iof.make_df(ind_cumulative['i'], drop_zero=True, metaprefix=None)
        cumulative_infows_df = iof.mass_energy_df(cumulative_infows_df, aggregate_consumed=True)
        cumulative_outflows_df = iof.make_df(ind_cumulative['o'], drop_zero=True, metaprefix=None)
        cumulative_outflows_df = iof.mass_energy_df(cumulative_outflows_df, aggregate_consumed=True)

        meta_df = iof.metadata_df(user=dat.user_data, name=f'{compare_industry_name}_comparison', 
                        level="Industry", scenario="n/a", product="n/a",
                        product_qty="n/a", energy_flows=dat.energy_flows)

        df_list = [meta_df, cumulative_infows_df, cumulative_outflows_df]
        sheet_list = ["meta", "inflows (cumulative)", "outflows (cumulative)"]

        df_dict = iof.nested_dicts(2)

        for flow in ind_annual:
            for factory in ind_annual[flow]:
                df = iof.make_df(ind_annual[flow][factory], drop_zero=False, sort=True, metaprefix=None)
                sheet_name = f'{factory} {flow}'
                df_dict[flow[0]][factory] = df
                df_list.append(df)
                sheet_list.append(sheet_name)
        
        iof.write_to_excel(df_list, sheet_list=sheet_list, filedir=dat.outdir, filename=filename)

        if type(compare_outflows) is list:
            for flow in compare_outflows:
                iof.plot_annual_flows(df_dict['o'], flow, dat.outdir, file_id=f"_{compare_industry_name}-comparison")

        if type(compare_inflows) is list:
            for flow in compare_outflows:
                iof.plot_annual_flows(df_dict['i'], flow, dat.outdir, file_id=f"_{compare_industry_name}-comparison")

    
        print(f"\n INDUSTRY COMPARISON - Full results available in {dat.outdir} directory.")



def main():
    pass

if __name__ == "__main__":
    main()