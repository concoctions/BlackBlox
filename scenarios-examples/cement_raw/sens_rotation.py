
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

from concrete_config import concrete_life
from concrete_config import r as orig_r
from concrete_config import  f_suffix, factory_names, f_kwargs
from concrete_config import concrete_factory, concrete_CCS_factory


def sens_rotation(CO2_dict, case_list=False, id=''):
    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')

    
    if case_list is False:
        case_list = list(CO2_dict.keys())

    print('...starting sensitivity analysis: biomass rotation')
    Path(f'{dat.outdir}/figures_sens/').mkdir(parents=True, exist_ok=True)

    net_CO2_dict = {}

    if id:
        id = id + '_'

    Rs = [1, 25, 50, 75, 100] 
    colors = ['#a1e3ff', '#77b0cd', '#4f7f9d', '#ffa746', '#002942']

    if orig_r > max(Rs):
        max_r = orig_r
    else:
        max_r = max(Rs)

    print('...using base case data from provided dictionary')

    case_list = [k for k in CO2_dict.keys()]
    fossil_dict = nested_dicts(3) #[c][y][flow] = float

    for c in case_list:   
        if 'BIO' not in c:
            fossil_dict[c] = CO2_dict.pop(c)
        else:
            CO2_dict[c]['totals']['net CO2'] = [0 for r in Rs]
            for t in range(1,  max_r+1):
                CO2_dict[c][t]['CO2 removed, biomass growth'] = [0 for r in Rs]

    


    ## CALCULATE biomass CO2 reuptake over time (Gaussian distribution)
    ##---------------------------

    for i,r in enumerate(Rs):
        

        for c in CO2_dict:

            if r == 1:
                CO2_dict[c][1]['CO2 removed, biomass growth'][i] = CO2_dict[c]['totals']['CO2 removed, biomass growth'] 
                total_reuptake = CO2_dict[c][1]['CO2 removed, biomass growth'][i]
            
            else:
                mu = r/2 # rotation period / 2
                sigma = mu/2 
                bio_CO2 = CO2_dict[c]['totals']['CO2 removed, biomass growth']
                total_reuptake = 0

                for t in range(1, r+1):
                    g = (1 / (sqrt(2 * pi * sigma**2))) * e ** ((-(t - mu) ** 2 ) / (2 * sigma ** 2))
                    CO2_uptake = g * bio_CO2 * (1/0.9543845676778868)  # correction factor as area under the curve for this formula does not equal 1 at the rotation period
                    CO2_dict[c][t]['CO2 removed, biomass growth'][i] = CO2_uptake
                    total_reuptake += CO2_uptake

    print("...biomass uptake data added.")




    ## GRAPH CO2-over-time 
    ##---------------------------
    
    CO2_emitted = []
    CO2_removed = []

    for c in CO2_dict:
        CO2_emitted.append(CO2_dict[c]['totals']['CO2 emitted, total'])
        CO2_removed.append(CO2_dict[c]['totals']['CO2 removed, total'])

    max_CO2 = max(CO2_emitted) * 1000
    min_CO2 = min(CO2_removed) * 1000 * -1

    ## Individual Cases
    
    for c in CO2_dict:
        if 'BIO' in c and 'CCS' not in c:
            c_fossil = c.replace('-BIO', '')
            c_BECCS = c + '-CCS'
            c_CCS = c_fossil + '-CCS'

            years = [k for k in CO2_dict[c] if k not in ['totals', 'meta']]
            plt.figure(figsize=(8,5))
            ax = plt.subplot(111)

            #biomass only
            CO2_fossil = []
            CO2_bio = []
            CO2_removed = []
            fossil_CO2_cum = []
            
            cum_CO2 = 0

            for y in years:
                fossil_CO2 = 0
                bio_CO2 = 0
                removed_CO2 = 0

                if y == 0:
                    fossil_CO2 += fossil_dict[c_fossil][y]['CO2 emitted, calcination'] + fossil_dict[c_fossil][y]['CO2 emitted, fossil (total)'] + fossil_dict[c_fossil][y]['CO2 emitted, upstream'] + fossil_dict[c_fossil][y]['CO2 emitted, infrastructure']
                    bio_CO2 += fossil_dict[c_fossil][y]['CO2 emitted, biogenic (total)']
                else:
                    removed_CO2 += (fossil_dict[c_fossil][y]['CO2 removed, concrete weathering'] + fossil_dict[c_fossil][y]['CO2 removed, biomass growth']) * -1
                    if y == concrete_life+1:
                        fossil_CO2 += fossil_dict[c_fossil][y]['CO2, demolition']

                CO2_fossil.append(fossil_CO2 * 1000)
                CO2_bio.append(bio_CO2 * 1000,)
                CO2_removed.append(removed_CO2 * 1000)
                cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                fossil_CO2_cum.append(cum_CO2)
            
            for i in range(len(Rs)):

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
                    else:
                        removed_CO2 += (CO2_dict[c][y]['CO2 removed, concrete weathering'] + CO2_dict[c][y]['CO2 removed, biomass growth'][i]) * -1
                        if y == concrete_life+1:
                            fossil_CO2 += CO2_dict[c][y]['CO2, demolition']

                    CO2_fossil.append(fossil_CO2 * 1000)
                    CO2_bio.append(bio_CO2 * 1000,)
                    CO2_removed.append(removed_CO2 * 1000)
                    cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                    CO2_cum.append(cum_CO2)
                    if y == years[-1]:
                        CO2_dict[c]['totals']['net CO2'][i] = cum_CO2
                        net_CO2_dict[f'{c} rotation {Rs[i]}'] = cum_CO2
                    
                    
                x = range(len(years))
                
                if i == 0:
                    ax.plot(x, CO2_cum, label="Bioenergy Only", color='none', linestyle='none')

                if i == orig_r:
                    ax.plot(x, CO2_cum, label=f"{Rs[i]}-year", color=colors[i], linestyle='dashed')
                else:
                    ax.plot(x, CO2_cum, label=f"{Rs[i]}-year", color=colors[i], linestyle='dashed')


            # BECCS
            CO2_fossil = []
            CO2_bio = []
            CO2_removed = []
            fossil_CO2_cum = []
            
            cum_CO2 = 0

            for y in years:
                fossil_CO2 = 0
                bio_CO2 = 0
                removed_CO2 = 0

                if y == 0:
                    fossil_CO2 += fossil_dict[c_CCS][y]['CO2 emitted, calcination'] + fossil_dict[c_CCS][y]['CO2 emitted, fossil (total)'] + fossil_dict[c_CCS][y]['CO2 emitted, upstream'] + fossil_dict[c_CCS][y]['CO2 emitted, infrastructure']
                    bio_CO2 += fossil_dict[c_CCS][y]['CO2 emitted, biogenic (total)']
                else:
                    removed_CO2 += (fossil_dict[c_CCS][y]['CO2 removed, concrete weathering'] + fossil_dict[c_CCS][y]['CO2 removed, biomass growth']) * -1
                    if y == concrete_life+1:
                        fossil_CO2 += fossil_dict[c_CCS][y]['CO2, demolition']

                CO2_fossil.append(fossil_CO2 * 1000)
                CO2_bio.append(bio_CO2 * 1000,)
                CO2_removed.append(removed_CO2 * 1000)
                cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                fossil_CO2_cum.append(cum_CO2)
            
            for i in range(len(Rs)):

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
                        fossil_CO2 += CO2_dict[c_BECCS][y]['CO2 emitted, calcination'] + CO2_dict[c_BECCS][y]['CO2 emitted, fossil (total)'] + CO2_dict[c_BECCS][y]['CO2 emitted, upstream'] + CO2_dict[c_BECCS][y]['CO2 emitted, infrastructure']
                        bio_CO2 += CO2_dict[c_BECCS][y]['CO2 emitted, biogenic (total)']
                    else:
                        removed_CO2 += (CO2_dict[c_BECCS][y]['CO2 removed, concrete weathering'] + CO2_dict[c_BECCS][y]['CO2 removed, biomass growth'][i]) * -1
                        if y == concrete_life+1:
                            fossil_CO2 += CO2_dict[c_BECCS][y]['CO2, demolition']

                    CO2_fossil.append(fossil_CO2 * 1000)
                    CO2_bio.append(bio_CO2 * 1000,)
                    CO2_removed.append(removed_CO2 * 1000)
                    cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                    CO2_cum.append(cum_CO2)
                    if y == years[-1]:
                        CO2_dict[c_BECCS]['totals']['net CO2'][i] = cum_CO2
                        net_CO2_dict[f'{c_BECCS} rotation {Rs[i]}'] = cum_CO2
                    
                    
                x = range(len(years))

                if i == 0:
                    ax.plot(x, CO2_cum, label="\nBECCS", color='none', linestyle='none')
                if i == orig_r:
                    ax.plot(x, CO2_cum, label=f"{Rs[i]}-year", color=colors[i], linestyle='dashdot')
                else:
                    ax.plot(x, CO2_cum, label=f"{Rs[i]}-year", color=colors[i], linestyle='dashdot')

            # ax.plot(x, fossil_CO2_cum, label=f"without bioenergy use", color='black', linestyle='dotted')  

            ax.axhline(y=0, color='grey')
            plt.yticks(np.arange(-100, 410, 50))
            plt.xticks(np.arange(0, 101, 10))
            plt.xlim(0,100)
            plt.ylim(-100,400)
            # plt.yticks(np.arange(round(min_CO2,-2)-50, round(max_CO2,-2)+50, 50))
            plt.ylabel('cumulative net CO$_2$ emissions,\nkg per m$^3$ concrete')
            plt.xlabel('years after concrete production and biomass replanting')
            plt.title(f'Sensitivity Analysis of Biomass Rotation Period,\ncase {c}\n')
            plt.subplots_adjust(right=0.6, bottom=0.25)
            plt.legend(bbox_to_anchor=(1.04,0.95), loc="upper left", fontsize="10", frameon=False)

            if c in case_list:
                plt.savefig(f'{dat.outdir}/figures_sens/{id}rotation_{c}.png')
            plt.close()

    print("...CO2 over time graphs created.")

    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')

    return net_CO2_dict
