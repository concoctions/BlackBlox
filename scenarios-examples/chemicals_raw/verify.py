from datetime import datetime
import blackblox.unitprocess as unit
import blackblox.factory as fac
from blackblox.io_functions import make_df

print("\n\n##################################################")
print("##################################################\n")

##################################################################

# NH3_stoich = unit.UnitProcess("NH3_stoich")

# NH3_stoich.balance(qty=(1.0),
#                     scenario='NH3-0',
#                     write_to_console=True)


# NH3_stoich.balance(qty=1.0,
#                     scenario='NH3-BIO',
#                     write_to_console=True)

# urea = unit.UnitProcess("urea")

# urea.balance(qty=94170,
#                     scenario='NH3-0',
#                     write_to_console=True)

# urea.balance(qty=94170,
#                     scenario='NH3-BIO',
#                     write_to_console=True)


# biogas = unit.UnitProcess("biogas")

# biogas.balance(qty=1.0,
#                     scenario='NH3-BIO',
#                     write_to_console=True)

# biomethane = unit.UnitProcess("biomethane")

# biomethane.balance(qty=1.0,
#                     scenario='NH3-BIO',
#                     write_to_console=True)

h2 = unit.UnitProcess("H2")
h2.balance(qty=85.1,
                    scenario='H2-0',
                    write_to_console=True)

# H2_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="H2")
# H2_factory.diagram(view=True, save=False)

# H2_factory.run_scenarios(scenario_list=['H2-0','H2-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)

# # FACTORY WITH CCS

# H2_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory_CCS.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="H2 with CCS")

# H2_factory_CCS.diagram(view=True, save=False)


# H2_factory_CCS.run_scenarios(scenario_list=['H2-0','H2-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)



# H2_factory_pure = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory_CCS-pure.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="H2 with CCS on pure CO2 onlt")

# H2_factory_pure.diagram(view=True, save=False)


# H2_factory_pure.run_scenarios(scenario_list=['H2-0','H2-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)



# H2_factory_flue = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory_CCS-flue.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="H2 with CCS on flue gas only")

# H2_factory_flue.diagram(view=True, save=False)


# H2_factory_flue.run_scenarios(scenario_list=['H2-0','H2-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)


# ETHANOL

## FACTORY WITHOUT CCS

# eth_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ethanol_factory.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ethanol")
# eth_factory.diagram(view=True, save=False)

# eth_factory.run_scenarios(scenario_list=['ETH-0','ETH-BIO'],
#                           product_qty=(3.95*1000), #3.95ktonne->tonne
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)




# eth_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ethanol_factory_CCS.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ethanol with CCS")

# eth_factory_CCS.diagram(view=True, save=False)

# eth_factory_CCS.run_scenarios(scenario_list=['ETH-0','ETH-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)




# eth_factory_pure_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ethanol_factory_CCS-pure.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ethanol with pure CO2 CCS")

# eth_factory_pure_CCS.diagram(view=True, save=False)

# eth_factory_pure_CCS.run_scenarios(scenario_list=['ETH-0','ETH-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)



# ## LIGNOCELLULOSIC ETHANOL 

# lth_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ligno_ethanol_factory.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Lignocellulosic Ethanol CCS")

# lth_factory.diagram(view=True, save=False)

# lth_factory.run_scenarios(scenario_list=['ETH-0','ETH-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)




# lth_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ligno_ethanol_factory_CCS.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                
#                   name="Lignocellulosic Ethanol CCS")
# lth_factory_CCS.diagram(view=True, save=False)

# lth_factory_CCS.run_scenarios(scenario_list=['ETH-0','ETH-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)




# lth_factory_CCS_pure = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ligno_ethanol_factory_CCS-pure.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Lignocellulosic Ethanol Pure CO2 CCS")
# lth_factory_CCS_pure.diagram(view=True, save=False)

# lth_factory_CCS_pure.run_scenarios(scenario_list=['ETH-0','ETH-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)

#  ## AMMONIA

# # FACTORY WITHOUT CCS

# NH3_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ammonia")
# NH3_factory.diagram(view=True, save=False)

# NH3_factory.run_scenarios(scenario_list=['NH3-0','NH3-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)

# # FACTORY WITH CCS

# NH3_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory_CCS.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ammonia with CCS")

# NH3_factory_CCS.diagram(view=True, save=False)


# NH3_factory_CCS.run_scenarios(scenario_list=['NH3-0','NH3-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)



# NH3_factory_pure = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory_CCS-pure.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ammonia with CCS on pure CO2 onlt")

# NH3_factory_pure.diagram(view=True, save=False)


# NH3_factory_pure.run_scenarios(scenario_list=['NH3-0','NH3-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)



# NH3_factory_flue = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory_CCS-flue.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ammonia with CCS on flue gas only")

# NH3_factory_flue.diagram(view=True, save=False)


# NH3_factory_flue.run_scenarios(scenario_list=['NH3-0','NH3-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)


# # UREA 

# Urea_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/Urea_factory.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Urea")
# Urea_factory.diagram(view=True, save=False)


# Urea_factory.run_scenarios(scenario_list=['NH3-0','NH3-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)

# # UREA FACTORY WITH CCS

# Urea_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/Urea_factory_CCS.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Urea with CCS")

# Urea_factory_CCS.diagram(view=True, save=False)


# Urea_factory_CCS.run_scenarios(scenario_list=['NH3-0','NH3-BIO'],
#                           product_qty=1.0,
#                           upstream_outflows=['CO2',], 
#                           downstream_outflows=['CO2',],
#                           upstream_inflows=['CO2 removed',],
#                           aggregate_flows=['CO2', 'CO2__upstream', 'CO2 removed', 'stored CO2'],                       
#                           net_flows=[('CO2', 'agg_o', 'CO2 removed', 'agg_i')],
#                           write_to_xls=True)



#####################################################################

print(f"\n({datetime.now().strftime('%H%M')}) Done.\n")
