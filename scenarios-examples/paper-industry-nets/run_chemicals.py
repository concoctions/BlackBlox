from pathlib import Path
from copy import deepcopy
from datetime import datetime
import blackblox.dataconfig as dat

import blackblox.factory as fac
from blackblox.io_functions import nested_dicts

from eth_cases import eth_cases
from nh3_cases import nh3_cases
from singlevar_sens import multi_sens


dat.path_outdir = f'{dat.path_outdir}/{dat.time_str}'
Path(dat.path_outdir).mkdir(parents=True, exist_ok=True)

dat.user_data = {
    "name": "S.E. Tanzer",
    "affiliation": "Delft Univeristy of Technology, Faculty of Technology, Policy, and Management",
    "project": "D-LCA of BECCS and Accelerated Carbonation in Concrete Production",
}

dat.default_emissions = ['CO2__fossil', 'CO2__bio', 'H2O', 'contrib - produced CO2__bio', 'contrib - produced CO2__fossil']



print(f'\n>--START--->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{datetime.now().strftime("%H%M")}\n')

sdict = nested_dicts(2)
sdict['transport']['variable'] = 'product transport'
sdict['transport']['options'] = [0, 100, 200, 300, 400,]
sdict['transport']['chain'] = ['ethanol']
sdict['transport']['unit'] = ['eth_box']
sdict['transport']['chain_CCS'] = ['ethanol']
sdict['transport']['unit_CCS'] = ['eth_box']
sdict['transport']['fixed vars'] = False
sdict['transport']['xticks'] = ['0', '100', '200', '300', '400',]
sdict['transport']['xlabel'] =  "product transport distance"
sdict['transport']['title'] = "net CO2"
sdict['transport']['vline-loc'] = 0
sdict['transport']['vline-label'] = ""

sdict_CO2 = nested_dicts(2)
sdict_CO2['co2-eff']['variable'] = 'Heat Demand'
sdict_CO2['co2-eff']['options'] = [2.8, 3.0, 3.2, 3.4, 3.6,]
sdict_CO2['co2-eff']['chain'] = ['CO2 Capture']
sdict_CO2['co2-eff']['unit'] =  ['simple_CO2capture']
sdict_CO2['co2-eff']['fixed vars'] = False
sdict_CO2['co2-eff']['xticks'] =  [2.8, 3.0, 3.2, 3.4, 3.6,]
sdict_CO2['co2-eff']['xlabel'] =  "GJ / t CO2 captured"
sdict_CO2['co2-eff']['title'] = "net CO2, by CO Capture heat demand"
sdict_CO2['co2-eff']['vline-loc'] = 2
sdict_CO2['co2-eff']['vline-label'] = ""

case_list = ['ETH-0', 'ETH-BIO']

f_kwargs = dict(
        product='C2H6O',
        product_qty = 1.0,
        upstream_outflows=['CO2', 'CO2 infrastructure'],
        upstream_inflows=['CO2 removed',],
        aggregate_flows=['CO2', 'CO2__fossil', 'CO2__bio', 'CO2__upstream', 'CO2 infrastructure'],
        )


# ETHANOL 

# Starch ethanol factories
eth_factory = fac.Factory(chain_list_file='data/chemicals/ethanol_factory.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='ethanol')
eth_CCS_factory = fac.Factory(chain_list_file='data/chemicals/ethanol_factory_CCS.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='ethanol-CCS')
eth_factory_pure_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ethanol_factory_CCS-pure.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="Ethanol pure CO2 CCS")
# eth_factory_flue_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/ethanol_factory_CCS-flue.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Ethanol flue CO2 CCS")


# starch ethanol parameters
eth_factory_list = [eth_factory,  
        eth_factory_pure_CCS, 
        # eth_factory_flue_CCS, 
        eth_CCS_factory,]
eth_suffix= ["", 
        "-pure CO2 CCS", 
        # "-flue CO2 CCS",
         "-full CCS"] #suffix for cases from each factory to identify it
eth_factory_names = [f.name for f in eth_factory_list]

# starch ethanol calculations
eth_cases("ethanol (maize)", eth_factory_list, eth_factory_names, eth_suffix, f_kwargs, case_list, feedstock='maize', fuel='stover')
multi_sens("ethanol (maize)", eth_factory_list, case_list, sdict)
multi_sens("ethanol (maize)", [eth_CCS_factory], case_list, sdict_CO2)



# lignocellulosic ethanol factories
leth_factory = fac.Factory(chain_list_file='data/chemicals/ligno_ethanol_factory.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='lingoethanol')
leth_CCS_factory = fac.Factory(chain_list_file='data/chemicals/ligno_ethanol_factory_CCS.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='lignoethanol-CCS')
leth_factory_pure_CCS = fac.Factory(chain_list_file='data/chemicals/ligno_ethanol_factory_CCS-pure.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='lignoethanol pure CO2 CCS')
# leth_factory_flue_CCS = fac.Factory(chain_list_file='data/chemicals/ligno_ethanol_factory_CCS-flue.xlsx',
#                     chain_list_sheet='chains', 
#                     connections_sheet='connections', 
#                     name='lignoethanol flue CO2 CCS')
# leth_factory_CCS_lignin = fac.Factory(chain_list_file='data/chemicals/ligno_ethanol_factory_CCS-lignin.xlsx',
#                     chain_list_sheet='chains', 
#                     connections_sheet='connections', 
#                     name='lignoethanol-CCS, lignin for CCS heat')


# lignocellulosic ethanol parameters
lth_factory_list = [leth_factory, 
                leth_factory_pure_CCS, 
                # leth_factory_flue_CCS, 
                leth_CCS_factory,] #leth_factory_CCS_lignin]
lth_factory_names = [f.name for f in lth_factory_list]
lth_suffix= ["", 
        "-pure CO2 CCS", 
        # "-flue CO2 CCS", 
        "-full CCS",] #"full CCS-lignin for heat"] 


# lignocellulosic ethanol calculations
eth_cases("ethanol (stover)", lth_factory_list, lth_factory_names, lth_suffix, f_kwargs, case_list, feedstock='stover', fuel='stover')

sdict['transport']['unit'] = ['lth_box']
sdict['transport']['unit_CCS'] = ['lth_box']
multi_sens("ethanol (stover)", lth_factory_list, case_list, sdict)
multi_sens("ethanol (stover)", [leth_CCS_factory], case_list, sdict_CO2)

# ###############################################################################

# AMMONIA & UREA 


# Ammonia Factories
NH3_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="NH3")
NH3_factory_pure = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory_CCS-pure.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="NH3 with CCS on pure CO2 only")
# NH3_factory_flue = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory_CCS-flue.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="NH3 with CCS on flue gas only")
NH3_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/NH3_factory_CCS.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="NH3 with CCS")


# # Ammonia parameters
NH3_case_list = ['NH3-0', 'NH3-BIO']

sdict['transport']['chain'] = ['NH3']
sdict['transport']['unit'] = ['NH3_stoich']
sdict['transport']['chain_CCS'] = ['NH3']
sdict['transport']['unit_CCS'] = ['NH3_stoich']

sdict_CO2['co2-eff']['unit'] =  ['duplicate_CO2capture']

f_kwargs['product'] = 'NH3'

NH3_factory_list = [NH3_factory, 
                NH3_factory_pure, 
                # NH3_factory_flue, 
                NH3_factory_CCS]

NH3_suffix= [ "", 
        "-pure CO2 CCS",
        #  "-flue CO2 CCS", 
         "-full CCS"] #suffix for cases from each factory to identify it
NH3_factory_names = [f.name for f in NH3_factory_list]

## Run Ammonia calculations
nh3_cases("NH3", NH3_factory_list, NH3_factory_names, NH3_suffix, f_kwargs, NH3_case_list)
multi_sens("NH3", NH3_factory_list, NH3_case_list, sdict)
multi_sens("NH3", [NH3_factory_CCS], NH3_case_list, sdict_CO2)


# Urea Factories
urea_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/Urea_factory.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="Urea")
# urea_factory_flue = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/Urea_factory_CCS-flue.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="Urea with CCS on flue gas only")
urea_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/Urea_factory_CCS.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="Urea with CCS")



urea_factory_list = [urea_factory, 
        # urea_factory_flue,
        urea_factory_CCS]
urea_suffix= [ "", 
        # "-flue CO2 CCS", 
        "-full CCS"] #suffix for cases from each factory to identify it
urea_factory_names = [f.name for f in urea_factory_list]
f_kwargs['product_qty'] =  0.625279101 #0.612238879 # 0.63944577  qty of NH3 required to produce 1 t of Urea (+ sufficient CO2 for urea)                                                      )

# Run Urea calculations
nh3_cases("Urea", urea_factory_list, urea_factory_names, urea_suffix, f_kwargs, NH3_case_list)
multi_sens("Urea", urea_factory_list, NH3_case_list, sdict)
multi_sens("Urea", [urea_factory_CCS], NH3_case_list, sdict_CO2)



#############################################################################
# HYDROGEN

# Hydrogen Factories
H2_factory = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="H2")
H2_factory_pure = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory_CCS-pure.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="H2 with CCS on pure CO2 only")
# H2_factory_flue = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory_CCS-flue.xlsx',
#                                  chain_list_sheet='chains', 
#                                  connections_sheet='connections', 
#                                  name="H2 with CCS on flue gas only")
H2_factory_CCS = fac.Factory(chain_list_file='/Users/Tanzer/GitHub/Industry-NETs-Paper/data/chemicals/H2_factory_CCS.xlsx',
                                 chain_list_sheet='chains', 
                                 connections_sheet='connections', 
                                 name="H2 with CCS")


# H2 parameters
H2_case_list = ['H2-0', 'H2-BIO']

sdict['transport']['chain'] = ['H2']
sdict['transport']['unit'] = ['H2']
sdict['transport']['chain_CCS'] = ['H2']
sdict['transport']['unit_CCS'] = ['H2']

f_kwargs['product'] = 'H2'
f_kwargs['product_qty'] = 1.0

H2_factory_list = [H2_factory, 
        H2_factory_pure, 
        # H2_factory_flue,
         H2_factory_CCS]
H2_suffix= [ "", 
        "-pure CO2 CCS", 
        # "-flue CO2 CCS", 
        "-full CCS"] #suffix for cases from each factory to identify it
H2_factory_names = [f.name for f in H2_factory_list]

# Run H2 calculations
nh3_cases("H2", H2_factory_list, H2_factory_names, H2_suffix, f_kwargs, H2_case_list)
multi_sens("H2", H2_factory_list, H2_case_list, sdict)
multi_sens("H2", [H2_factory_CCS], H2_case_list, sdict_CO2)

print(f'\n{datetime.now().strftime("%H%M")}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<--END---<\n')
