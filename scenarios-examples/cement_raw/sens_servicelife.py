
"""Modelling for time-specific life cycle assessment of concrete production
    with various cases of bioenergy and CCS use (in cement production) and 
    accelerated carbonation in concrete curing.

Author: Ir. S.E. Tanzer
Affiliation: Delft Univeristy of Technology, Faculty of Technology, Policy, and
    Management
Date Created: 23 October 2020
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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pan

from concrete_config import m3_concrete, concrete_life, EoL_calc, demo_CO2_LCI, r, k, k_cmu, A, A_cmu, DOC
from concrete_config import case_list, factory_list, f_suffix, factory_names, f_kwargs
from concrete_config import concrete_factory, concrete_CCS_factory


def sens_servicelife(CO2_dict, case_list=False, id=''):
    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')

    print('...starting sensitivity analysis: concrete service life')
    Path(f'{dat.outdir}/figures_sens/').mkdir(parents=True, exist_ok=True)

    if case_list is False:
        case_list = list(CO2_dict.keys())

    if id:
        id = id + '_'

    net_CO2_dict = {}

    years = [25, 50, 75, 100, 200]
    labels = ['25 years', '50 years', '75 years', '100 years', '200 years']

    colors = ['#002942', '#ffa746', '#4f7f9d', '#77b0cd', '#a1e3ff']

    print('...using base case data from provided dictionary')

    for c in CO2_dict:
        CO2_dict[c]['totals']['CO2 removed, total']  = [CO2_dict[c]['totals']['CO2 removed, biomass growth'] for y in years]
        
        CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'] = [0 for y in years]

        CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition']  = [0 for y in years]

        CO2_dict[c]['totals']['net CO2'] = [0 for y in years]
        
        for t in range(1, 202):
            CO2_dict[c][t]['CO2 removed, concrete weathering'] = [0 for y in years]


    ## CALCULATE cement weathering CO2 uptake over time
    ##---------------------------

    for i in range(len(years)):
        k_A_DOC = 0
        if id.startswith('cmu'):
            for j in range(len(k_cmu)):
                k_A_DOC += k_cmu[j] * A_cmu[j] * DOC[j]
        else:
            for j in range(len(k)):
                k_A_DOC += k[j] * A[j] * DOC[j]

        for c in CO2_dict:
            calc_CO2 = CO2_dict[c]['totals']['calcinated CO2'] 

            total_CO2 = 0

            # generate adjustment factor for accelerated carbonation
            AC_CO2 = CO2_dict[c]['totals']['CO2 in concrete, accelerated carbonation']
            if AC_CO2 > 0:
                t_adjust = ((AC_CO2 / k_A_DOC /  (calc_CO2/m3_concrete)) * 1000) ** 2 
            else:
                t_adjust = 0

            for t in range(1, years[i]+1):           
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

                CO2_dict[c][t]['CO2 removed, concrete weathering'][i] = CO2_uptake

            CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'][i] = total_CO2
            CO2_dict[c]['totals']['CO2 removed, total'][i] += total_CO2


        ## CALCULATE cement demolition CO2 emissions and weathering
        ##---------------------------

        for i in range(len(years)):
            for c in CO2_dict:
                CO2_dict[c][years[i]+1]['CO2, demolition'] = [0 for i in range(len(years))]
                demo_CO2 = CO2_dict[c]['totals']['concrete, mass'] * demo_CO2_LCI # ecoinvent 3.5 demolition factor
                CO2_dict[c][years[i]+1]['CO2, demolition'][i] = demo_CO2
                
                calc_CO2 = CO2_dict[c]['totals']['calcinated CO2'] 

                max_CO2_reuptake = EoL_calc * calc_CO2

                CO2_in_concrete = CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'][i] + CO2_dict[c]['totals']['CO2 in concrete, accelerated carbonation']

                if max_CO2_reuptake > CO2_in_concrete:
                    demo_weathering = max_CO2_reuptake - CO2_in_concrete
                else:
                    demo_weathering = 0

                CO2_dict[c][years[i]+1]['CO2 removed, concrete weathering'][i] = demo_weathering
                CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition'][i] = demo_weathering
                CO2_dict[c]['totals']['CO2 removed, total'][i] += demo_weathering

    print("...concrete wethering and demolition data added.")




    ## GRAPH CO2-over-time 
    ##---------------------------
    
    CO2_emitted = []
    CO2_removed = []

    for c in CO2_dict:
        CO2_emitted.append(CO2_dict[c]['totals']['CO2 emitted, total'])
        CO2_removed.extend(CO2_dict[c]['totals']['CO2 removed, total'])

    max_CO2 = max(CO2_emitted) * 1000
    min_CO2 = min(CO2_removed) * 1000 * -1


    ## Individual Cases
    
    for c in CO2_dict:

        life_years = [k for k in CO2_dict[c] if k not in ['totals', 'meta']]
        plt.figure()
        ax = plt.subplot(111)
        
        for i in range(len(years)):

            CO2_fossil = []
            CO2_bio = []
            CO2_removed = []
            CO2_cum = []
            
            cum_CO2 = 0

            for y in (life_years):
                fossil_CO2 = 0
                bio_CO2 = 0
                removed_CO2 = 0

                if y == 0:
                    fossil_CO2 += CO2_dict[c][y]['CO2 emitted, calcination'] + CO2_dict[c][y]['CO2 emitted, fossil (total)'] + CO2_dict[c][y]['CO2 emitted, upstream'] + CO2_dict[c][y]['CO2 emitted, infrastructure']
                    bio_CO2 += CO2_dict[c][y]['CO2 emitted, biogenic (total)']
                else:
                    removed_CO2 += (CO2_dict[c][y]['CO2 removed, concrete weathering'][i] + CO2_dict[c][y]['CO2 removed, biomass growth']) * -1
                    if y == years[i]+1:
                        fossil_CO2 += CO2_dict[c][y]['CO2, demolition'][i]

                CO2_fossil.append(fossil_CO2 * 1000)
                CO2_bio.append(bio_CO2 * 1000,)
                CO2_removed.append(removed_CO2 * 1000)
                cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                CO2_cum.append(cum_CO2)
                if y == life_years[-1]:
                    CO2_dict[c]['totals']['net CO2'][i] = cum_CO2
                    net_CO2_dict[f'{c} servicelife {labels[i]}'] = cum_CO2
                
            x = range(len(life_years))
            
            ax.plot(x, CO2_cum, label=f"{labels[i]}", color=colors[i])
                
        ax.axhline(y=0, linestyle='dashed')
        plt.yticks(np.arange(round(min_CO2,-2)-50, round(max_CO2,-2)+50, 50))

        plt.ylabel('cumulative net CO$_2$ emissions, kg per m$^3$ concrete')
        plt.xlabel('years')
        plt.title(f'Sensitivity Analysis of Concrete Service Life,\ncase {c}')
        plt.legend()

        if c in case_list:
            plt.savefig(f'{dat.outdir}/figures_sens/{id}servicelife_{c}.png')
        plt.close()

    print("...CO2 over time graphs created.")

    
    ## export totals
    ##----------------
    w =  pan.ExcelWriter(f"{dat.outdir}/{id}servicelife_sens_{dat.time}.xlsx")

    for c in CO2_dict:
        rows = [] # years
        cols = ['when']
        cols.extend(labels)
        
        r = ['net CO2, total (kg/m3)'] 
        r.extend([ i for i  in CO2_dict[c]['totals']['net CO2']])
        rows.append(r)

        r = ['CO2 removed, total (kg/m3)'] 
        r.extend([i * 1000 for i in CO2_dict[c]['totals']['CO2 removed, total']])
        rows.append(r)

        r = ['CO2 removed, service life (kg/m3)']
        r.extend([i * 1000 for i0 in CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life']])
        rows.append(r)

        r = ['calcination CO2 (kg/m3)']
        r.extend([CO2_dict[c]['totals']['calcinated CO2'] * 1000 for i in CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life']])
        rows.append(r)

        r = ['CO2 removed by service life weathering, prct of calc CO2'] 
        prct = [ i/CO2_dict[c]['totals']['calcinated CO2'] * 100 for i in CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life']]
        r.extend(prct)
        rows.append(r)

        r = ['CO2 removed, concrete weathering, demolition (kg/m3)']
        r.extend([i * 1000 for i in CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition']])
        rows.append(r)

        for t in range(1, 200+2):
            r =[f"year {t}"]
            r.extend([i * 1000 for i in CO2_dict[c][t]['CO2 removed, concrete weathering']])
            rows.append(r)

        df = pan.DataFrame(rows, columns=cols)
        df = df.set_index('when')
        
        df.to_excel(w, sheet_name=c)
        w.save()
  
    print("...exposure sensitivity totals to file.")

    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')
    
    return net_CO2_dict