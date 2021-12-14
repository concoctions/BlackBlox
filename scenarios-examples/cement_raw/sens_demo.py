
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

from concrete_config import m3_concrete, concrete_life, EoL_calc, demo_CO2_LCI, r
from concrete_config import case_list, factory_list, f_suffix, factory_names, f_kwargs
from concrete_config import concrete_factory, concrete_CCS_factory


def sens_demo(CO2_dict, case_list=False, id=''):
    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')

    if case_list is False:
        case_list = list(CO2_dict.keys())

    print('...starting sensitivity analysis: demolition carbonation')
    Path(f'{dat.outdir}/figures_sens/').mkdir(parents=True, exist_ok=True)

    if id:
        id = id + '_'

    net_CO2_dict = {}

    DOCs = [0, 0.20, 0.40, 0.60, 0.80]
    labels = ['none', 'to 20%', 'to 40%', 'to 60%', 'to 80%']
    colors = ['#ffa746', '#29526e', '#4f7f9d', '#4f7f9d', '#a1e3ff',]

    print('...using base case data from provided dictionary')

    for c in CO2_dict:
        CO2_dict[c]['totals']['CO2 removed, total'] = [CO2_dict[c]['totals']['CO2 removed, total'] - CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition'] for d in DOCs]
        CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition']  = [0 for D in DOCs]
        CO2_dict[c]['totals']['net CO2'] = [0 for D in DOCs]
        
        for t in range(1, concrete_life+2):
            CO2_dict[c][t]['CO2 removed, concrete weathering'] = [CO2_dict[c][t]['CO2 removed, concrete weathering'] for D in DOCs]

    ## CALCULATE cement weathering CO2 uptake over time
    ##---------------------------

    for i in range(len(DOCs)):

        ## CALCULATE cement demolition CO2 emissions and weathering
        ##---------------------------

        for c in CO2_dict:
            calc_CO2 = CO2_dict[c]['totals']['calcinated CO2'] 

            max_CO2_reuptake = calc_CO2 * DOCs[i]

            CO2_in_concrete = CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'] + CO2_dict[c]['totals']['CO2 in concrete, accelerated carbonation']

            if max_CO2_reuptake > CO2_in_concrete:
                demo_weathering = max_CO2_reuptake - CO2_in_concrete
            else:
                demo_weathering = 0

            CO2_dict[c][concrete_life+1]['CO2 removed, concrete weathering'][i] = demo_weathering
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

        years = [k for k in CO2_dict[c] if k not in ['totals', 'meta']]
        plt.figure()
        ax = plt.subplot(111)
        
        for i in range(len(DOCs)):

            CO2_fossil = []
            CO2_bio = []
            CO2_removed = []
            CO2_cum = []
            net_CO2 = []
            
            cum_CO2 = 0

            for y in years:
                fossil_CO2 = 0
                bio_CO2 = 0
                removed_CO2 = 0

                if y == 0:
                    fossil_CO2 += CO2_dict[c][y]['CO2 emitted, calcination'] + CO2_dict[c][y]['CO2 emitted, fossil (total)'] + CO2_dict[c][y]['CO2 emitted, upstream'] + CO2_dict[c][y]['CO2 emitted, infrastructure']
                    bio_CO2 += CO2_dict[c][y]['CO2 emitted, biogenic (total)']
                else:
                    removed_CO2 += (CO2_dict[c][y]['CO2 removed, concrete weathering'][i] + CO2_dict[c][y]['CO2 removed, biomass growth']) * -1
                    if y == concrete_life+1:
                        fossil_CO2 += CO2_dict[c][y]['CO2, demolition']

                CO2_fossil.append(fossil_CO2 * 1000)
                CO2_bio.append(bio_CO2 * 1000,)
                CO2_removed.append(removed_CO2 * 1000)
                cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                CO2_cum.append(cum_CO2)
                if y == years[-1]:
                    CO2_dict[c]['totals']['net CO2'][i] = cum_CO2
                    net_CO2_dict[f'{c} demolition {labels[i]}'] = cum_CO2
                
            x = range(len(years))
            
            ax.plot(x, CO2_cum, label=f"{labels[i]} of calcination CO$_2$", color=colors[i])
                
        ax.axhline(y=0, linestyle='dashed')
        plt.yticks(np.arange(round(min_CO2,-2)-50, round(max_CO2,-2)+50, 50))

        plt.ylabel('cumulative net CO$_2$ emissions, kg per m$^3$ concrete')
        plt.xlabel('years')
        plt.title(f'Sensitivity analysis of concrete weathering during demolition,\ncase {c}')
        plt.legend()

        if c in case_list:
            plt.savefig(f'{dat.outdir}/figures_sens/{id}demolition_{c}.png')
        plt.close()

    print("...CO2 over time graphs created.")

    
    ## export totals
    ##----------------
    w =  pan.ExcelWriter(f"{dat.outdir}/{id}demo_sens_{dat.time}.xlsx")

    for c in CO2_dict:
        rows = [] # years
        cols = ['when']
        cols.extend(labels)

        r = ['net CO2, total (kg/m3)'] 
        r.extend([i for i in CO2_dict[c]['totals']['net CO2']])
        rows.append(r)

        r = ['CO2 removed, total (kg/m3)'] 
        r.extend([i * 1000 for i in CO2_dict[c]['totals']['CO2 removed, total']])
        rows.append(r)

        r = ['CO2 removed, service life (kg/m3)']
        r.extend([CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'] * 1000 for i in CO2_dict[c]['totals']['net CO2']])
        rows.append(r)

        r = ['calcination CO2 (kg/m3)']
        r.extend([CO2_dict[c]['totals']['calcinated CO2'] * 1000 for i in CO2_dict[c]['totals']['net CO2']])
        rows.append(r)

        r = ['CO2 removed, concrete weathering, demolition (kg/m3)']
        r.extend([i * 1000 for i in CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition']])
        rows.append(r)

        df = pan.DataFrame(rows, columns=cols)
        df = df.set_index('when')
        
        df.to_excel(w, sheet_name=c)
        w.save()
  
    print("...demolition sensitivity totals to file.")

    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')

    return net_CO2_dict