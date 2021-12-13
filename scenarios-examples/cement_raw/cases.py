
"""Modelling for time-specific life cycle assessment of concrete production
    with various cases of bioenergy and CCS use (in cement production) and 
    accelerated carbonation in concrete curing.

Author: Ir. S.E. Tanzer
Affiliation: Delft Univeristy of Technology, Faculty of Technology, Policy, and
    Management
Date Created: 8 October 2020
Date Last Modified (code or data): 23 October 2020 

"""

# add blackblox to Path (needed until I package it properly)
from pathlib import Path
import sys
sys.path.append('/Users/Tanzer/GitHub/BlackBlox/')

import blackblox.unitprocess as unit
import blackblox.processchain as cha
import blackblox.factory as fac
import blackblox.dataconfig as dat
from blackblox.io_functions import make_df
from blackblox.io_functions import nested_dicts

from datetime import datetime
from math import sqrt
from math import pi
from math import e
from pandas import ExcelWriter
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator
import matplotlib.transforms as mtrans

from concrete_config import m3_concrete, concrete_life, k, k_cmu, A, A_cmu, DOC, demo_CO2_LCI, r
from concrete_config import EoL_calc as EoL_calc_default
from concrete_config import case_list, factory_list, f_suffix, factory_names, f_kwargs

def base_cases(case_list=case_list, id='', factory_list=factory_list, f_suffix=f_suffix, factory_names=factory_names,
                reflines=None, order=False, case_labels=False, id_groups=False, group_names=False):

    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')
    print(f'...generating cases{case_list} for {factory_names}')

    dat.default_scenario = "BASE"

    if 'cement' in id:
        c_type = 'Portland Cement'
    elif '30mpa' in id:
        c_type = 'Ordinary Portland Concrete, 30mpa'
    elif 'cmu' in id:
        c_type = 'Concrete Masonry Units'
    else:
        c_type = "Concrete"
    id = id + '_'


    ## RUN all cases and get data
    ##---------------------------
    CO2_dict = nested_dicts(3) # CO2_dict[case][year][CO2_type]


    for i in range(len(factory_list)):

        multi_i, multi_o, multi_ai, multi_ao, multi_n =  factory_list[i].run_scenarios(case_list, **f_kwargs, write_to_xls=True)

        # drop mass/energy index
        multi_i = multi_i.reset_index(level=0, drop=True)
        multi_o = multi_o.reset_index(level=0, drop=True)


    ## PRINT factory totals to console
    ##---------------------------------

        # print("\nIN FLOWS\n", multi_i)
        # print("\nOUT FLOWS\n", multi_o)
        # print("\nAGG IN FLOWS\n", multi_ai)
        # print("\nAGG OUT FLOWS\n", multi_ao)

        # print("\n\n")


    ## GET data for each case
    ##---------------------------------

        for j, c in enumerate(case_list):
            case = c+f_suffix[i]
            
            CO2_dict[case]['meta']['subgraph x'] = j
            CO2_dict[case]['meta']['subgraph y'] = i

            # get total flows
            CO2_dict[case]['totals']['CO2 emitted, total'] = multi_ao.loc['CO2', c]
            CO2_dict[case]['totals']['calcinated CO2'] = multi_o.loc['calcination CO2', c.lower()]

            if 'concrete' in multi_o.index:
                CO2_dict[case]['totals']['concrete, mass'] = multi_o.loc['concrete', c.lower()]

            #get contributing flows
            bio = False
            DAC = False
            if 'CO2__bio' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, biogenic (total)'] = multi_o.loc['CO2__bio', c.lower()] 
                if 'CO2__bio-fuel production' in multi_o.indiex:
                    CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += multi_o.loc['CO2__bio-fuel production', c.lower()]
                bio = True
                if 'contrib kiln - CO2 bio' in multi_o.index:
                    CO2_dict[case]['totals']['CO2 produced, biogenic'] += multi_o.loc['contrib kiln - CO2 bio', c.lower()]
                if 'contrib-charcoal - CO2 bio' in multi_o.index:
                    CO2_dict[case]['totals']['CO2 produced, biogenic'] += multi_o.loc['contrib-charcoal - CO2 bio', c.lower()]
                if 'contrib heat CCS - CO2 bio'  in multi_o.index:
                    CO2_dict[case]['totals']['CO2 produced, biogenic'] += multi_o.loc['contrib heat CCS - CO2 bio', c.lower()]

            if 'contrib_CO2__bio-annual' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, biogenic, annual'] = multi_o.loc['contrib_CO2__bio-annual', c.lower()]
            CO2_dict[case][0]['CO2 emitted, fossil (total)'] = multi_o.loc['CO2__fossil', c.lower()]
            CO2_dict[case][0]['CO2 emitted, upstream'] = multi_ao.loc['CO2__upstream', c]
            if 'CO2__upstream (transport - lorry (tkm))' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, upstream, of which transport'] = multi_o.loc['CO2__upstream (transport - lorry (tkm))', c.lower()] + multi_o.loc['CO2__upstream (transport - rail (tkm))', c.lower()] 
            CO2_dict[case][0]['CO2 emitted, infrastructure'] = multi_ao.loc['CO2 infrastructure', c]
            CO2_dict[case][0]['CO2 emitted, fossil, of which electricity'] = multi_o.loc['contrib-electricity - CO2 fossil', c.lower()] 

            # flows that do not appear in all factories/cases        
            if 'concrete CO2 content' in multi_o.index:
                CO2_dict[case]['totals']['CO2 in concrete, accelerated carbonation'] = multi_o.loc['concrete CO2 content', c.lower()]
                CO2_dict[case]['totals']['stored CO2'] += multi_o.loc['concrete CO2 content', c.lower()]
            if 'contrib AC losses - CO2 fossil' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, fossil, of which AC losses'] = multi_o.loc['contrib AC losses - CO2 fossil', c.lower()]
            if 'contrib AC losses - CO2 bio' in multi_o.index:    
                CO2_dict[case][0]['CO2 emitted, biogenic, of which AC losses'] = multi_o.loc['contrib AC losses - CO2 bio', c.lower()]
            if 'CO2__calcination' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, calcination'] = multi_o.loc['CO2__calcination', c.lower()]

            if 'contrib kiln - CO2 fossil' in multi_o.index:
                CO2_dict[case][0]['CO2 produced, fossil, of which cement kiln fuel'] = multi_o.loc['contrib kiln - CO2 fossil' , c.lower()] 
            if 'contrib-charcoal - CO2 bio' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, biogenic, of which charcoal'] = multi_o.loc['contrib-charcoal - CO2 bio', c.lower()]
            if 'contrib kiln - CO2 bio' in multi_o.index:    
                CO2_dict[case][0]['CO2 produced, biogenic, of which cement kiln fuel'] = multi_o.loc['contrib kiln - CO2 bio', c.lower()]

            if 'stored CO2' not in multi_o.index:
                if 'contrib kiln - CO2 fossil' in multi_o.index:
                    CO2_dict[case][0]['CO2 emitted, fossil, of which cement kiln fuel'] = multi_o.loc['contrib kiln - CO2 fossil' , c.lower()] 
                if 'contrib kiln - CO2 bio' in multi_o.index:
                    CO2_dict[case][0]['CO2 emitted, biogenic, of which cement kiln fuel'] = multi_o.loc['contrib kiln - CO2 bio', c.lower()]

            if 'CO2__lost - CCS (AC)' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, fossil, of which AC CO2 capture'] += multi_o.loc['CO2__lost - CCS (AC)' , c.lower()] 
                CO2_dict[case][0]['CO2 emitted, fossil (total)'] += CO2_dict[case][0]['CO2 emitted, fossil, of which AC CO2 capture']
                CO2_dict[case][0]['CO2 emitted, fossil, of which AC CO2 capture'] += multi_o.loc['contrib heat CCS AC- CO2 fossil' , c.lower()] 

            if 'stored CO2' in multi_o.index:
                CO2_dict[case]['totals']['stored CO2'] += multi_o.loc['stored CO2', c.lower()]
                CO2_dict[case][0]['CO2 emitted, upstream, of which transport'] += multi_o.loc['CO2__upstream (transport - pipeline onshore  (tkm))', c.lower()]

            if 'contrib heat CCS - CO2 fossil' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, fossil, of which heat for CCS'] =  multi_o.loc['contrib heat CCS - CO2 fossil', c.lower()]
                           
            if 'contrib heat CCS - CO2 bio' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, biogenic, of which heat for CCS'] =  multi_o.loc['contrib heat CCS - CO2 bio', c.lower()]     

            if 'contrib-electricity CCS - CO2 fossil' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, fossil, of which electricity for CCS'] =  multi_o.loc['contrib-electricity CCS - CO2 fossil', c.lower()] 

            if 'stored CO2' in multi_o.index:
                # breakdown of CO2 to capture by fuel type
                if 'contrib kiln - CO2 fossil' in multi_o.index:
                    CO2_dict[case][0]['CO2 to capture, fossil'] = multi_o.loc['contrib kiln - CO2 fossil' , c.lower()] 
                    CO2_dict[case][0]['CO2 stored, fossil'] = CO2_dict[case][0]['CO2 to capture, fossil'] * (0.9 - (0.9*0.01))

                if 'contrib kiln - CO2 bio' in multi_o.index:
                    CO2_dict[case][0]['CO2 to capture, biogenic'] = multi_o.loc['contrib kiln - CO2 bio', c.lower()]
                    CO2_dict[case][0]['CO2 stored, biogenic'] = CO2_dict[case][0]['CO2 to capture, biogenic'] * (0.9 - (0.9*0.01)) # capture eff + transport losses)
                
                CO2_dict[case][0]['CO2 to capture, calcination'] = multi_o.loc['calcination CO2', c.lower()]
                CO2_dict[case][0]['CO2 stored, calcination'] = CO2_dict[case][0]['CO2 to capture, calcination'] * (0.9 - (0.9*0.01)) # capture eff + transport losses)
                CO2_to_Capture = CO2_dict[case][0]['CO2 to capture, fossil'] + CO2_dict[case][0]['CO2 to capture, biogenic'] + CO2_dict[case][0]['CO2 to capture, calcination']

                CO2_dict[case][0]['CO2 emitted, fossil, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()] * (CO2_dict[case][0]['CO2 to capture, fossil']/ CO2_to_Capture )
                CO2_dict[case][0]['CO2 emitted, fossil (total)'] += CO2_dict[case][0]['CO2 emitted, fossil, of which CCS loss']

                CO2_dict[case][0]['CO2 emitted, biogenic, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()]  * (CO2_dict[case][0]['CO2 to capture, biogenic']/ CO2_to_Capture )
                CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += CO2_dict[case][0]['CO2 emitted, biogenic, of which CCS loss']

                CO2_dict[case][0]['CO2 emitted, calcination, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()]  * (CO2_dict[case][0]['CO2 to capture, calcination']/ CO2_to_Capture )
                CO2_dict[case][0]['CO2 emitted, calcination'] += CO2_dict[case][0]['CO2 emitted, calcination, of which CCS loss']
            
            #if atmospheric co2 in concrete 
            if 'contrib - atm CO2 captured' in multi_o.index:
                CO2_dict[case]['totals']['CO2 removed, DAC'] += multi_o.loc['contrib - atm CO2 captured', c.lower()]
                CO2_dict[case]['totals']['CO2 removed, total'] += CO2_dict[case]['totals']['CO2 removed, DAC']
                DAC = True

            if 'contrib AC CO2 bio - in concrete' in multi_o.index:
                CO2_dict[case]['totals']['CO2 removed, total'] += multi_o.loc['contrib AC CO2 bio - in concrete', c.lower()]
                CO2_dict[case][0]['CO2 emitted, biogenic, annual'] += multi_o.loc['contrib AC CO2 bio - in concrete', c.lower()]


            CO2_dict[case]['totals']['electricity use (kWh)'] += multi_o.loc['CONSUMED electricity', c.lower()] * 277.778
            
            if 'dry cleft timber' in multi_i.index:
                CO2_dict[case]['totals']['timber'] += multi_i.loc['dry cleft timber', c.lower()]
            
            if 'dry wood chips (EU no swiss)' in multi_i.index:
                CO2_dict[case]['totals']['timber'] += multi_i.loc['dry wood chips (EU no swiss)', c.lower()]
    
    print("...all cases run.")

    for key in ['10AC_bioAC-DAC', '10AC_bioAC-CCS-flue', '10AC_bioAC-CCS-ownCO2', 
                'CMU15AC_bioAC-DAC', 'CMU15AC_bioAC-CCS-flue', 'CMU15AC_bioAC-CCS-ownCO2']:
        if key in CO2_dict:
            CO2_dict.pop(key)

    ## CALCULATE cement weathering CO2 uptake over time
    ##---------------------------

    if 'cement' not in id:
        for c in CO2_dict:
            k_A_DOC = 0

            calc_CO2 = CO2_dict[c]['totals']['calcinated CO2'] 

            total_CO2 = 0

            if 'cmu' in c.lower():
                for i in range(len(k_cmu)):
                    k_A_DOC += k_cmu[i] * A_cmu[i] * DOC[i]
            else:
                for i in range(len(k)):
                    k_A_DOC += k[i] * A[i] * DOC[i]

            # generate adjustment factor for accelerated carbonation
            AC_CO2 = CO2_dict[c]['totals']['CO2 in concrete, accelerated carbonation']
            if AC_CO2 > 0:
                t_adjust = ((AC_CO2 / k_A_DOC /  (calc_CO2/m3_concrete)) * 1000) ** 2 
            else:
                t_adjust = 0

            for t in range(1, concrete_life+1):           
                if t == 1:
                    if t_adjust > 0: # adjust for CO2 already present due to accelerated carbonation
                        CO2_uptake_adjust = k_A_DOC * (sqrt(t_adjust)/1000) * (calc_CO2/m3_concrete)
                        CO2_uptake = k_A_DOC * (sqrt(t+t_adjust)/1000) * (calc_CO2/m3_concrete) - CO2_uptake_adjust
                    else:
                        CO2_uptake = k_A_DOC * (sqrt(t+t_adjust)/1000) * (calc_CO2/m3_concrete)
                else:
                    if t_adjust > 0: # adjust for CO2 already present due to accelerated carbonation 
                        CO2_uptake = k_A_DOC * (sqrt(t+t_adjust)/1000) * (calc_CO2/m3_concrete) - total_CO2  - CO2_uptake_adjust
                    else:
                        CO2_uptake = k_A_DOC * (sqrt(t+t_adjust)/1000) * (calc_CO2/m3_concrete) - total_CO2

                total_CO2 += CO2_uptake

                CO2_dict[c][t]['CO2 removed, concrete weathering'] = CO2_uptake

            CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'] = total_CO2
            CO2_dict[c]['totals']['CO2 removed, total'] += total_CO2

        print("...concrete weathering data added.")
    else:
        k_A_DOC = 0


    ## CALCULATE cement demolition CO2 emissions and weathering
    ##---------------------------

    if 'cement' not in id:
        for c in CO2_dict:
            if 'opt' in c:
                EoL_calc = 0.75
            elif '2018' in c:
                EoL_calc = 0
            else:
                EoL_calc = EoL_calc_default

            demo_CO2 = CO2_dict[c]['totals']['concrete, mass'] * demo_CO2_LCI # ecoinvent 3.5 demolition factor
            CO2_dict[c][concrete_life+1]['CO2, demolition'] = demo_CO2
            CO2_dict[c]['totals']['CO2 emitted, total'] += demo_CO2

            calc_CO2 = CO2_dict[c]['totals']['calcinated CO2'] 

            max_CO2_reuptake = EoL_calc * calc_CO2

            CO2_in_concrete = CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'] + CO2_dict[c]['totals']['CO2 in concrete, accelerated carbonation']

            if max_CO2_reuptake > CO2_in_concrete:
                demo_weathering = max_CO2_reuptake - CO2_in_concrete
            else:
                demo_weathering = 0

            CO2_dict[c][concrete_life+1]['CO2 removed, concrete weathering'] = demo_weathering
            CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition'] = demo_weathering
            CO2_dict[c]['totals']['CO2 removed, total'] += demo_weathering

        print("...concrete demolition data added.")
    else:
        EoL_calc = 0

    ## CALCULATE biomass CO2 reuptake over time (Gaussian distribution)
    ##---------------------------


    mu = r/2 # rotation period / 2
    sigma = mu/2 

    for c in CO2_dict:
        CO2_dict[c][1]['CO2 removed, biomass growth'] += CO2_dict[c][0]['CO2 emitted, biogenic, annual']
        CO2_dict[c]['totals']['CO2 removed, biomass growth'] += CO2_dict[c][0]['CO2 emitted, biogenic, annual']
        CO2_dict[c]['totals']['CO2 removed, total'] += CO2_dict[c][0]['CO2 emitted, biogenic, annual']

        bio_CO2 = CO2_dict[c]['totals']['CO2 produced, biogenic'] - CO2_dict[c][0]['CO2 emitted, biogenic, annual']

        total_uptake = 0

        for t in range(1, r+1):
            g = (1 / (sqrt(2 * pi * sigma**2))) * e ** ((-(t - mu) ** 2 ) / (2 * sigma ** 2))
            CO2_uptake = g * bio_CO2 * (1/0.9543845676778868)  # correction factor as area under the curve for this formula does not equal 1 at the rotation period
            CO2_dict[c][t]['CO2 removed, biomass growth'] += CO2_uptake
            total_uptake += CO2_uptake

        CO2_dict[c]['totals']['CO2 removed, biomass growth'] += total_uptake
        CO2_dict[c]['totals']['CO2 removed, total'] += total_uptake

    print("...biomass uptake data added.")


    ## WRITE TO FILE Totals Data
    ##---------------------------

    meta_dict = {'all cases': {
                'Concrete service life': concrete_life,
                'Biomass rotation period': r,
                'Fraction of CaO carbonated after demolition': EoL_calc,
                'k * a * DOC': k_A_DOC,
                'demolition CO2 LCI': demo_CO2_LCI
                }} 

    totals_dict = nested_dicts(2)
    gate_dict = nested_dicts(2)
    demo_dict = nested_dicts(2)

    CO2_generated = []
    CO2_emitted = []
    CO2_removed = []

    # totals dicts
    for c in CO2_dict:
        totals_dict[c] = CO2_dict[c]['totals']
        totals_dict[c]['net CO2'] = (totals_dict[c]['CO2 emitted, total'] - totals_dict[c]['CO2 removed, total'])
        gate_dict[c] = CO2_dict[c][0]
        demo_dict[c] = CO2_dict[c][concrete_life + 1]
        CO2_emitted.append(totals_dict[c]['CO2 emitted, total'])
        CO2_removed.append(totals_dict[c]['CO2 removed, total'])
        CO2_generated.append(totals_dict[c]['CO2 emitted, total'] + totals_dict[c]['stored CO2'])


    # c-balance dicts

    balance_dict = nested_dicts(2)

    for c in CO2_dict:
        d = CO2_dict[c]

        # net CO2
        balance_dict[c][' net CO2'] =  d['totals']['CO2 emitted, total'] - d['totals']['CO2 removed, total']  
        balance_dict[c][' net CO2, checksum'] = round(totals_dict[c]['net CO2'],8) == round(balance_dict[c][' net CO2'],8)
        
        # emitted CO2
        balance_dict[c]['emitted CO2'] = d[0]['CO2 emitted, biogenic (total)'] + \
                                        d[0]['CO2 emitted, fossil (total)'] + \
                                        d[0]['CO2 emitted, calcination'] + \
                                        d[0]['CO2 emitted, infrastructure'] + \
                                        d[0]['CO2 emitted, upstream'] + \
                                        d[concrete_life+1]['CO2, demolition']
        balance_dict[c]['emitted CO2, checksum'] = round(d['totals']['CO2 emitted, total'],8) == round(balance_dict[c]['emitted CO2'],8)

        # removed CO2    
        balance_dict[c]['removed CO2'] = d['totals']['CO2 removed, biomass growth'] + \
                                        d['totals']['CO2 removed, concrete weathering, service life'] + \
                                        d['totals']['CO2 removed, concrete weathering, demolition']
        balance_dict[c]['removed CO2, checksum'] = round(d['totals']['CO2 removed, total'],8) == round(balance_dict[c]['removed CO2'],8)
            
        # stored CO2    
        balance_dict[c]['stored CO2 (year 0)'] = d[0]['CO2 stored, fossil'] + \
                                        d[0]['CO2 stored, biogenic'] + \
                                        d[0]['CO2 stored, calcination'] + \
                                        d['totals']['CO2 in concrete, accelerated carbonation']
        balance_dict[c]['stored CO2, checksum'] = round(d['totals']['stored CO2'],8) == round(balance_dict[c]['stored CO2 (year 0)'],8)

        # CO2 in concrete = 
        balance_dict[c]['CO2 in concrete (end-of-life)'] = d['totals']['CO2 in concrete, accelerated carbonation'] + \
                                                        d['totals']['CO2 removed, concrete weathering, service life'] + \
                                                        d['totals']['CO2 removed, concrete weathering, demolition']

        # biogenic CO2
        balance_dict[c]['biogenic CO2, IN'] = d[0]['CO2 produced, biogenic, of which cement kiln fuel'] + \
                                            d[0]['CO2 emitted, biogenic, of which charcoal'] + \
                                            d[0]['CO2 emitted, biogenic, of which heat for CCS']
                                                # d[0]['CO2 emitted, biogenic, of which CCS loss'] 

        balance_dict[c]['biogenic CO2, OUT'] =  d[0]['CO2 emitted, biogenic, of which charcoal'] + \
                                                d[0]['CO2 emitted, biogenic, of which heat for CCS'] + \
                                                d[0]['CO2 emitted, biogenic, of which cement kiln fuel'] + \
                                                d[0]['CO2 emitted, biogenic, of which CCS loss'] +  \
                                                d[0]['CO2 stored, biogenic']
        balance_dict[c]['biogenic CO2, checksum'] = round(balance_dict[c]['biogenic CO2, IN'],8) == round(balance_dict[c]['biogenic CO2, OUT'], 8) == round(d['totals']['CO2 removed, biomass growth'], 8)
            
        # fossil CO2  
        balance_dict[c]['fossil CO2, IN'] = d[0]['CO2 produced, fossil, of which cement kiln fuel'] + \
                                            d[0]['CO2 emitted, fossil, of which electricity'] + \
                                            d[0]['CO2 emitted, fossil, of which electricity for CCS'] + \
                                            d[0]['CO2 emitted, fossil, of which heat for CCS'] + \
                                            d[0]['CO2 emitted, fossil, of which AC CO2 capture']+ \
                                            d[0]['CO2 emitted, fossil, of which AC losses'] 

        balance_dict[c]['fossil CO2, OUT'] = d[0]['CO2 emitted, fossil, of which CCS loss'] + \
                                            d[0]['CO2 emitted, fossil, of which cement kiln fuel'] + \
                                            d[0]['CO2 emitted, fossil, of which electricity'] + \
                                            d[0]['CO2 emitted, fossil, of which electricity for CCS'] + \
                                            d[0]['CO2 emitted, fossil, of which heat for CCS'] + \
                                            d[0]['CO2 emitted, fossil, of which AC CO2 capture'] + \
                                            d[0]['CO2 emitted, fossil, of which AC losses'] + \
                                            d[0]['CO2 stored, fossil']

        balance_dict[c]['fossil CO2, checksum'] = round(balance_dict[c]['fossil CO2, IN'],8) == round(balance_dict[c]['fossil CO2, OUT'], 8)

        # calcination CO2
        balance_dict[c]['calcination CO2, IN'] = d['totals']['calcinated CO2']
        balance_dict[c]['calcination CO2, OUT'] = d[0]['CO2 emitted, calcination'] + d[0]['CO2 stored, calcination']
        balance_dict[c]['calcination CO2, checksum'] = round(balance_dict[c]['calcination CO2, IN'],8) == round(balance_dict[c]['calcination CO2, OUT'], 8)

        #updownstream CO2
        balance_dict[c]['updownstream CO2'] = d[0]['CO2 emitted, infrastructure'] + \
                                                d[0]['CO2 emitted, upstream'] + \
                                                d[concrete_life+1]['CO2, demolition']

        #carbonation CO2
        balance_dict[c]['carbonation CO2, natural'] = d['totals']['CO2 removed, concrete weathering, service life'] + \
                                            d['totals']['CO2 removed, concrete weathering, demolition'] 
        balance_dict[c]['carbonation CO2, accelerated'] = d['totals']['CO2 in concrete, accelerated carbonation']

        if 'opt' not in c and '2018' not in c:
            balance_dict[c]['carbonation CO2, checksum'] = round(balance_dict[c]['carbonation CO2, natural']  + balance_dict[c]['carbonation CO2, accelerated'], 8) == round(0.6 * balance_dict[c]['calcination CO2, IN'],8) == round(balance_dict[c]['CO2 in concrete (end-of-life)'], 8)
        elif 'opt' in c: 
            balance_dict[c]['carbonation CO2, checksum'] = round(balance_dict[c]['carbonation CO2, natural']  + balance_dict[c]['carbonation CO2, accelerated'], 8) == round(0.75 * balance_dict[c]['calcination CO2, IN'],8) == round(balance_dict[c]['CO2 in concrete (end-of-life)'], 8)
        else:
            balance_dict[c]['carbonation CO2, checksum'] = round(balance_dict[c]['carbonation CO2, natural']  + balance_dict[c]['carbonation CO2, accelerated'], 8) == round(balance_dict[c]['CO2 in concrete (end-of-life)'], 8)

    for c in balance_dict:
        for key in balance_dict[c]:
            if 'checksum' in key:
                if balance_dict[c][key] == 1:
                    balance_dict[c][key] = 'TRUE'
                else: 
                    balance_dict[c][key] = 'FALSE'
                    print(c, key, balance_dict[c][key])
                    


    meta_df = make_df(meta_dict).sort_index()
    totals_df = make_df(totals_dict).sort_index()
    balance_df = make_df(balance_dict)
    gate_df = make_df(gate_dict).sort_index()
    demo_df = make_df(demo_dict).sort_index()


    with ExcelWriter(f"{dat.outdir}/{id}totalsOverTime_{dat.time}.xlsx") as writer:  
        meta_df.to_excel(writer, sheet_name='meta')
        totals_df.to_excel(writer, sheet_name='totals')
        gate_df.to_excel(writer, sheet_name='production')
        demo_df.to_excel(writer, sheet_name='demolition')
        balance_df.to_excel(writer, sheet_name='balance')


    print("...totals data writ to file")


    # GRAPH CO2-over-time 
    #---------------------------

    if order is False:
        order = list(CO2_dict.keys())
    
    if case_labels is False:
        case_labels = list(CO2_dict.keys())

    max_CO2 = round(max(CO2_generated) * 1000,-2) + 100
    min_CO2 = round(min(CO2_removed) * 1000 * -1, -2) - 100

    # Where to save figures
    fig_path = f'{dat.outdir}/figures_base'
    Path(fig_path).mkdir(parents=True, exist_ok=True) 


    if id_groups is False:
        if '30mpa' in id:
            id_groups = ['BASE', '03', '10']
            group_names = ['No Accelerated Carbonation', '0.3% CO$_2$ injection', '10% CO$_2$ curing']
        elif 'cmu' in id:
            id_groups = [ 'None', '15']
            group_names = ['No Accelerated Carbonation', '15% CO$_2$ curing']
        else:
            id_groups = ['None', '2050 not opt', '2050']
            group_names = ['current', 'future', 'future, optimsitic']
        

    if 'double' in id:
        fig, axs = plt.subplots(len(id_groups), 2, figsize=(9, len(id_groups)*3))
    else:
        fig, axs = plt.subplots(len(id_groups), figsize=(6, len(id_groups)*4))


    if len(id_groups) > 2:
        lw = 2
    else:
        lw = 1   

    for i, group in enumerate(id_groups):
        q = 0
        for j, c in enumerate(order):
            col = 0
            if 'CMU' in c:
                col = 1
                
            in_group = False
            if group is 'None':
                if not any(g in c for g in id_groups):
                    in_group = True
            elif type(group) is list:
                if c in group:
                    in_group = True
            elif group.startswith('not'):
                if group[4:] not in c:
                    in_group = True
            elif group is '2050 not opt':
                if '2050' in c and 'opt' not in c:
                    in_group = True
            elif group is 'benchmark':
                if '2018' not in c and '2050' not in c:
                    in_group = True
            elif group in c:
                in_group = True

            if in_group is True:

                years = [key for key in CO2_dict[c] if key not in ['totals', 'meta']]

                CO2_fossil = []
                CO2_bio = []
                CO2_removed = []
                CO2_cum = []
                
                cum_CO2 = 0

                for y in years:
                    fossil_CO2 = 0
                    bio_CO2 = 0
                    removed_CO2 = 0

                    if y == 0:
                        fossil_CO2 += CO2_dict[c][y]['CO2 emitted, calcination'] + CO2_dict[c][y]['CO2 emitted, fossil (total)'] + CO2_dict[c][y]['CO2 emitted, upstream'] + CO2_dict[c][y]['CO2 emitted, infrastructure']
                        bio_CO2 += CO2_dict[c][y]['CO2 emitted, biogenic (total)']
                        removed_CO2 += CO2_dict[c]['totals']['CO2 removed, DAC']
                    else:
                        removed_CO2 += (CO2_dict[c][y]['CO2 removed, concrete weathering'] + CO2_dict[c][y]['CO2 removed, biomass growth']) * -1
                        if y == concrete_life+1:
                            fossil_CO2 += CO2_dict[c][y]['CO2, demolition']

                    CO2_fossil.append(fossil_CO2 * 1000)
                    CO2_bio.append(bio_CO2 * 1000,)
                    CO2_removed.append(removed_CO2 * 1000)
                    cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                    CO2_cum.append(cum_CO2)
                

                x = range(len(years))
                
                if 'BIO' in c and 'CCS' in c:
                    label = 'BECCS'
                    color = '#ff9100'
                    ls = 'dashdot'
                elif 'CCS' in c:
                    label = 'CCS only'
                    color = '#46305a' 
                    ls = 'dashed'
                elif 'BIO' in c:
                    label = 'Bioenergy\nonly'
                    color = '#c53f64'
                    ls = 'dotted'
                else:
                    label = 'No CCS or\nbioenergy'
                    color = '#000408'
                    ls = 'solid'

                if i == len(id_groups)-1: 

                    if 'double' in id and 'CMU' in c:
                        axs[i, col].plot(x, CO2_cum, label=label, color=color, linestyle=ls, linewidth=lw)
                    elif 'double' in id:
                        axs[i, col].plot(x, CO2_cum, color=color, linestyle=ls, linewidth=lw) 
                    else:
                        axs[i].plot(x, CO2_cum, label=label, color=color, linestyle=ls, linewidth=lw)      
                else:
                    if 'double' in id:
                        axs[i, col].plot(x, CO2_cum, color=color, linestyle=ls, linewidth=lw) 
                    else:
                        axs[i].plot(x, CO2_cum, color=color, linestyle=ls, linewidth=lw) 
                q += 1
                if q == 4:
                    q = 0

        if 'double' in id:
            for cx in [0,1]:
                axs[i, cx].axhline(y=451, color='none')
                axs[i, cx].grid(True, which='both')
                axs[i, cx].axhline(y=0, color='grey')
                axs[i, cx].set_title(group_names[i])
                axs[i, cx].set_yticks(np.arange(-100, 410, 100))
                axs[i, cx].set_xticks(np.arange(0, 51, 5))
                axs[i, cx].set_ylim(ymin=-100, ymax=450)
                axs[i, cx].set_xlim(xmin=0, xmax=51)
                minor_locator = AutoMinorLocator(2)
                axs[i, cx].yaxis.set_minor_locator(minor_locator)
            

        else:
            axs[i].grid(True, which='both')
            # axs[i].axhline(y=451, color='none')
            axs[i].axhline(y=0, color='grey')
            axs[i].set_title(group_names[i])
            # axs[i].set_xlabel('year')
            axs[i].set_yticks(np.arange(-100, 410, 100))
            axs[i].set_xticks(np.arange(0, 51, 5))
            axs[i].set_ylim(ymin=-110, ymax=450)
            axs[i].set_xlim(xmin=0, xmax=51)
            # axs[i].minorticks_on()
            minor_locator = AutoMinorLocator(2)
            axs[i].yaxis.set_minor_locator(minor_locator)

        # if i == 0:
        #     axs[i].set_ylabel('cumulative net CO$_2$\nkg CO$_2$ per m$^3$ concrete')

    trans = mtrans.blended_transform_factory(fig.transFigure,mtrans.IdentityTransform())
    if 'double' in id:
        txt = fig.text(0.07, 0.53, "cumulative net CO$_2$ in kg CO$_2$ per m$^3$ concrete", ha='right',va='center', rotation='vertical', fontsize=12)
        txt2 = fig.text(0.5, 25, "years after concrete production", ha='center', fontsize=12)
        txt2.set_transform(trans)
        txt3 = fig.text(0.29, 0.95, 'Ordinary Portland Concrete (30mpa)', ha='center', fontsize=12, weight='bold')
        txt3 = fig.text(0.66, 0.95, 'Concrete Masonry Units', ha='center', fontsize=12, weight='bold')
        plt.legend(loc="upper right", bbox_to_anchor=(1.5,2.0), frameon=False)
        plt.subplots_adjust(left=0.12, bottom=0.08, right=0.82, top=0.9, wspace=0.2, hspace=0.25)

    else:
        txt = fig.text(0.07, 0.53, "cumulative net CO$_2$ in kg CO$_2$ per m$^3$ concrete", ha='right',va='center', rotation='vertical', fontsize=12)
        txt2 = fig.text(0.45, 80, "years after concrete production", ha='center', fontsize=12)
        txt2.set_transform(trans)
        plt.legend(loc="upper right", bbox_to_anchor=(1.4,2.0), frameon=False)
        plt.subplots_adjust(left=0.15, bottom=0.08, right=0.75, top=0.95, wspace=0, hspace=0.25)

    plt.savefig(f'{fig_path}/_{id}OverTime.png', dpi=200)
    plt.close()
    print("...CO2 over time graphs created.")



    ## GRAPH CO2 Contribution Chart
    ##---------------------------
    plt.figure(figsize=(9,5))

    CO2_upstream = []
    CO2_calc = []
    CO2_fossil = [] # fossil CO2 not from electricity (fuel combustion)
    CCS_fossil = []
    CO2_bio = []
    CCS_bio = []
    CO2_electricity = [] # electricity CO2
    CO2_removed_concrete = []
    CO2_removed_bio = []
    CO2_removed_DAC = []
    CO2_stored = []
    net_CO2 = []

    net_CO2_dict = dict()

    # arrange data into lists

    for c in order:
        d = CO2_dict[c]

        # CO2 emissions
        CO2_upstream.append((d[0]['CO2 emitted, upstream'] + d[0]['CO2 emitted, infrastructure']) * 1000)
        CO2_fossil.append((d[0]['CO2 emitted, fossil (total)'] - d[0]['CO2 emitted, fossil, of which electricity'] + d[concrete_life+1]['CO2, demolition'] - d[0]['CO2 emitted, fossil, of which electricity for CCS'] - d[0]['CO2 emitted, fossil, of which heat for CCS']) * 1000)
        CCS_fossil.append((d[0]['CO2 emitted, fossil, of which electricity for CCS'] + d[0]['CO2 emitted, fossil, of which heat for CCS']) * 1000)
        CO2_bio.append((d[0]['CO2 emitted, biogenic (total)'] - d[0]['CO2 emitted, biogenic, of which heat for CCS']) * 1000)
        CCS_bio.append(d[0]['CO2 emitted, biogenic, of which heat for CCS'] * 1000)
        CO2_calc.append(d[0]['CO2 emitted, calcination'] * 1000)
        CO2_electricity.append(d[0]['CO2 emitted, fossil, of which electricity'] * 1000)

        # CO2 removals
        CO2_removed_concrete.append((d['totals']['CO2 removed, concrete weathering, service life'] + d['totals']['CO2 removed, concrete weathering, demolition'] + d['totals']['CO2 removed, DAC']) * -1 * 1000)
        CO2_removed_bio.append(d['totals']['CO2 removed, biomass growth'] * -1 * 1000)
        CO2_removed_DAC.append(d['totals']['CO2 removed, DAC'])

        CO2_stored.append(d['totals']['stored CO2'] * 1000)

        # net CO2
        net_CO2.append((d['totals']['CO2 emitted, total'] - d['totals']['CO2 removed, total']) * 1000)
        net_CO2_dict[c] = (d['totals']['CO2 emitted, total'] - d['totals']['CO2 removed, total']) * 1000

    # Add positive values
    data = np.array([CO2_fossil, CO2_electricity, CCS_fossil,
                    CO2_calc,
                    CO2_bio, CCS_bio,
                    CO2_upstream,
                    CO2_stored
                    ])

    bar_labels = ["emitted, fossil\nconcrete production and demolition", "emitted, fossil\nelectricity for concrete production", "emitted, fossil\nCCS heat and electricity",
                  "emitted, fossil\ncalcination", 
                  "emitted, biogenic\nconcrete production", "emitted, biogenic\nCCS heat and electricity",
                  "emitted, upstream", "stored geologically or\nvia accelerated carbonation\n(i.e. generated but not emitted)"]

    color_list = ['#002942', '#002942', '#002942',
                  '#4a3f70',
                  '#9f4a7f', '#9f4a7f', 
                  '#e5626a', 'none']

    hatch = ['', '||||', '////',
             '',
             '', '////',
             '', '////']      

    hatch_color = [None, 'white', 'white',
                   None,  
                   None, 'white', 
                   None, '#f9cb5f']

    edgecolor_list = ['white', 'none', 'none',
                    'white', 
                    'white', 'none', 
                    'white', '#f9cb5f']

    width =[0.8, 0.8, 0.8,
            0.8, 
            0.8, 0.8,
            0.8, 0.7]

    if len(order) < 8:
        width[-1] = 0.75

    linestyles = ['-', '-', '-', 
                  '-',
                  '-', '-',
                  '-', (0, (5, 5)) ]


    X = np.arange(data.shape[1])

    for i in reversed(range(data.shape[0])):
        plt.bar(X, data[i],
            width = width[i],
            bottom = np.sum(data[:i], axis = 0),
            color = color_list[i % len(color_list)],
            label = bar_labels[i],
            hatch = hatch[i],
            edgecolor = hatch_color[i],
            ls = linestyles[i]
            )
        
        plt.bar(X, data[i],
            width = width[i],
            bottom = np.sum(data[:i], axis = 0),
            color = 'none',
            edgecolor = edgecolor_list[i],
            ls = linestyles[i]
            )            

    if DAC is False:
        data = np.array([CO2_removed_concrete,
                        CO2_removed_bio,
                        ])

    if DAC is True:
        data = np.array([CO2_removed_concrete,
                        CO2_removed_bio,
                        CO2_removed_DAC])

    bar_labels = ["removed via concrete weathering", "removed via biomass growth", 'removed via direct air capture']

    color_list = ['#006674', '#2ea572', '#d0d65a']

    # Add negative values
    X = np.arange(data.shape[1])

    for i in range(data.shape[0]):
        plt.bar(X, data[i],
        bottom = np.sum(data[:i], axis = 0),
        color = color_list[i % len(color_list)],
        label = bar_labels[i],
        edgecolor = 'white')

    plt.plot(net_CO2, linestyle="", marker="s", label="net CO$_2$ at end of service life\n(emissions minus removals)", color="#f3eb85", markeredgewidth=1.0, markeredgecolor='white')

    # zip joins x and y coordinates in pairs
    
    for x,y in zip(X,[int(round(n, -1)) for n in net_CO2]):

        label = f"{y}"

        plt.annotate(label, # this is the text
                    (x,y), # this is the point to label
                    textcoords="offset points", # how to position the text
                    xytext=(0,0), # distance from text to points (x,y)
                    color='#002942',
                    bbox=dict(boxstyle="square",
                    pad=0.15,
                    ec='white',
                    fc='#f3eb85',),
                    ha='center',
                    va='center',
                    fontsize=8,
                    weight='semibold') # horizontal alignment can be left, right or center

    # add formatting
    plt.axhline(0, color='grey')

    idx = np.asarray([i for i in range(len(case_labels))])
    plt.xticks(ticks=idx, labels=case_labels, rotation=90, fontsize="8.5", ha='center', va='top', multialignment='right')
    plt.legend(loc="upper right", fontsize="8.5", bbox_to_anchor=(1.45,1.02)) # bbox_to_anchor=(2.3,1.01))
    plt.subplots_adjust(left=0.1, right=0.7, bottom=0.3)

    if 'cement' in id:
        plt.ylabel(f"kg CO$_2$ per t cement")
        plt.yticks(np.arange(-800, 1200, 200))
   
    else:
        plt.ylabel(f"kg CO$_2$ per m$^3$ concrete")
        plt.yticks(np.arange(-400, 600, 100))
        plt.ylim(ymin=-400, ymax=600)

    plt.title(f"CO$_2$ balance over life cycle of {c_type}\n")

    plt.savefig(f'{fig_path}/_{id}Contribution.png', dpi=200)
    plt.close()

    print("...CO2 contributions graphs created.")



    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')

    return CO2_dict, net_CO2_dict

    