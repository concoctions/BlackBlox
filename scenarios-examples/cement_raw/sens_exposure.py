
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

from concrete_config import m3_concrete, concrete_life, demo_CO2_LCI, r
from concrete_config import EoL_calc as EoL_calc_default
from concrete_config import case_list, factory_list, f_suffix, factory_names, f_kwargs
from concrete_config import concrete_factory, concrete_CCS_factory


def sens_exposure(CO2_dict, id=''):
    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')

    print('...starting sensitivity analysis: concrete exposure')
    Path(f'{dat.outdir}/figures_sens/').mkdir(parents=True, exist_ok=True)

    if id:
        id = id + '_'

    net_CO2_dict = {}

    if id.startswith('cmu'):
        Ks = [1.1, 2.7, 6.9, 9.9, 6.6,]
    else:
        Ks = [0.8, 1.6, 4.6, 6.6, 4.4,]
    if id.startswith('cmu'):
        A = 9.4*2
    else:
        A = 5*2
    DOCs = [0.85, 0.85, 0.4, 0.4, 0.75,]
    labels = ['in ground', 'outdoor,\nexposed', 'indoor,\ncovered', 'indoor,\nexposed', 'outdoor,\nsheltered', 'benchmark']
    dict_labels = ['in ground', 'outdoor, exposed', 'indoor, covered', 'indoor, exposed', 'outdoor, sheltered', 'benchmark']
    colors = ['#002942', '#29526e', '#4f7f9d', '#77b0cd', '#a1e3ff', '#ffa746']

    print('...using base case data from provided dictionary')

    for c in CO2_dict:
        orig_total = CO2_dict[c]['totals']['CO2 removed, total']
        CO2_dict[c]['totals']['CO2 removed, total']  = [CO2_dict[c]['totals']['CO2 removed, biomass growth'] for k in Ks]
        CO2_dict[c]['totals']['CO2 removed, total'].append(orig_total)
        
        orig_total = CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life']
        CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'] = [0 for k in Ks]
        CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'].append(orig_total)

        orig_total = CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition'] 
        CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition']  = [0 for k in Ks]
        CO2_dict[c]['totals']['CO2 removed, concrete weathering, demolition'].append(orig_total )

        orig_total = CO2_dict[c]['totals']['net CO2']
        CO2_dict[c]['totals']['net CO2'] = [0 for k in Ks]
        CO2_dict[c]['totals']['net CO2'].append(orig_total)
        
        for t in range(1, concrete_life+2):
            orig_total = CO2_dict[c][t]['CO2 removed, concrete weathering']
            CO2_dict[c][t]['CO2 removed, concrete weathering'] = [0 for k in Ks]
            CO2_dict[c][t]['CO2 removed, concrete weathering'].append(orig_total)


    ## CALCULATE cement weathering CO2 uptake over time
    ##---------------------------

    for i in range(len(Ks)):
        k_A_DOC = 0

        k_A_DOC += Ks[i] * A * DOCs[i]

        for c in CO2_dict:
            calc_CO2 = CO2_dict[c]['totals']['calcinated CO2'] 

            total_CO2 = 0

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

                CO2_dict[c][t]['CO2 removed, concrete weathering'][i] = CO2_uptake

            CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'][i] = total_CO2
            CO2_dict[c]['totals']['CO2 removed, total'][i] += total_CO2


        ## CALCULATE cement demolition CO2 emissions and weathering
        ##---------------------------

        for c in CO2_dict:
            calc_CO2 = CO2_dict[c]['totals']['calcinated CO2'] 

            if '2050' in c:
                if 'opt' in c:
                    EoL_calc = 0.75
            elif '2018' in c:
                EoL_calc = 0
            else:
                EoL_calc = EoL_calc_default
            max_CO2_reuptake = EoL_calc * calc_CO2

            CO2_in_concrete = CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life'][i] + CO2_dict[c]['totals']['CO2 in concrete, accelerated carbonation']

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



    # grouped subplots

    mpa30_subplots = [['BASE', 'BASE-BIO', 'BASE-CCS', 'BASE-BIO-CCS'], 
                    #   ['10AC_StrGain', '10AC-BIO_StrGain', '10AC_StrGain-CCS', '10AC-BIO_StrGain-CCS'],
                    #   ['2050-RM', '2050-RM-BIO', '2050-RM-CCS', '2050-RM-BIO-CCS'], 
                    #   ['2050-RM-opt', '2050-RM-BIO-opt', '2050-RM-opt-CCS', '2050-RM-BIO-opt-CCS'],
                    #   ['2050-10AC-opt_StrGain', '2050-10AC-BIO-opt_StrGain', '2050-10AC-opt_StrGain-CCS', '2050-10AC-BIO-opt_StrGain-CCS']
                      ]

    cmu_subplots = [['CMU', 'CMU-BIO', 'CMU-CCS', 'CMU-BIO-CCS'], 
                    #   ['CMU15AC_StrGain', 'CMU15AC-BIO_StrGain', 'CMU15AC_StrGain-CCS', 'CMU15AC-BIO_StrGain-CCS'],
                    #   ['2050-CMU', '2050-CMU-BIO', '2050-CMU-CCS', '2050-CMU-BIO-CCS'], 
                    #   ['2050-CMU-opt', '2050-CMU-BIO-opt', '2050-CMU-opt-CCS', '2050-CMU-BIO-opt-CCS'],
                    #   ['2050-CMU-opt_StrGain',  '2050-CMU15AC-BIO-opt_StrGain', '2050-CMU-opt_StrGain-CCS',  '2050-CMU15AC-BIO-opt_StrGain-CCS']
                      ]



    years = [k for k in CO2_dict[c] if k not in ['totals', 'meta']]
    linestyles = ['solid', 'dashed', 'dotted', 'dashdot']
    group_id = ['base', 'AC', '2050', '2050-opt', '2050AC-opt']
    
    if 'cmu' in id:
        subplot_list = cmu_subplots
    else:
        subplot_list = mpa30_subplots

    for p, sp in enumerate(subplot_list):
        plt.figure(figsize=(8, 5))
        ax = plt.subplot(111)
        for n, c in enumerate(sp):
        
            for i in range(len(Ks)+1):

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
                        net_CO2_dict[f'{c} exposure {dict_labels[i]}'] = cum_CO2
                    
                x = range(len(years))
                
                if n == 0:
                    ax.plot(x, CO2_cum, label=f"{labels[i]}", color=colors[i], linestyle=linestyles[n])
                else:
                    ax.plot(x, CO2_cum, color=colors[i], linestyle=linestyles[n])
            
        ax.axhline(y=0, color='grey')
        ax.set_yticks(np.arange(-100, 410, 50))
        ax.set_xticks(np.arange(0, 51, 5))
        ax.set_ylim(ymin=-100, ymax=400)
        ax.set_xlim(xmin=0, xmax=51)
        # plt.yticks(np.arange(round(min_CO2,-2)-50, round(max_CO2,-2)+50, 50))

        plt.ylabel('cumulative net CO$_2$ emissions,\nkg per m$^3$ concrete')
        plt.xlabel('\nyears after concrete production')
        plt.title(f'Sensitivity Analysis of Concrete Exposure Conditions,\n{group_id[p]}\n')
        plt.subplots_adjust(right=0.6, bottom=0.25)
        plt.legend(bbox_to_anchor=(1.04,0.95), loc="upper left", fontsize="10", frameon=False)
        # plt.legend(loc="upper right", bbox_to_anchor=(1.4,0.4), frameon=False)
        # plt.subplots_adjust(left=0.10, bottom=0.15, right=0.7, top=0.85, wspace=0, hspace=0.15)

        plt.savefig(f'{dat.outdir}/figures_sens/{id}exposure_{group_id[p]}.png')
        plt.close()

    print("...CO2 over time graphs created.")


    for c in CO2_dict:
        plotted = False
        for p in subplot_list:
            if c in p:
                plotted = True
        if plotted is False:
            for i in range(len(Ks)+1):

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
                        removed_CO2 += (CO2_dict[c][y]['CO2 removed, concrete weathering'] [i] + CO2_dict[c][y]['CO2 removed, biomass growth']) * -1
                        if y == concrete_life+1:
                            fossil_CO2 += CO2_dict[c][y]['CO2, demolition']

                    CO2_fossil.append(fossil_CO2 * 1000)
                    CO2_bio.append(bio_CO2 * 1000,)
                    CO2_removed.append(removed_CO2 * 1000)
                    cum_CO2 += ((fossil_CO2 + bio_CO2 + removed_CO2)*1000)
                    CO2_cum.append(cum_CO2)
                    if y == years[-1]:
                        CO2_dict[c]['totals']['net CO2'][i] = cum_CO2
                        net_CO2_dict[f'{c} exposure {dict_labels[i]}'] = cum_CO2



    
    ## export totals
    ##----------------
    w =  pan.ExcelWriter(f"{dat.outdir}/{id}exposure_sens_{dat.time}.xlsx")

    for c in CO2_dict:
        rows = [] # years
        cols = ['when']
        cols.extend(dict_labels)
        
        r = ['net CO2, total (kg/m3)'] 
        r.extend([i for i in CO2_dict[c]['totals']['net CO2']])
        rows.append(r)

        r = ['CO2 removed, total (kg/m3)'] 
        r.extend([i * 1000 for i in CO2_dict[c]['totals']['CO2 removed, total']])
        rows.append(r)

        r = ['CO2 removed, service life (kg/m3)']
        r.extend([i * 1000 for i in CO2_dict[c]['totals']['CO2 removed, concrete weathering, service life']])
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

        for t in range(1, concrete_life+2):
            r =[f"year {t}"]
            r.extend([i * 1000 for i in CO2_dict[c][t]['CO2 removed, concrete weathering']])
            rows.append(r)

        df = pan.DataFrame(rows, columns=cols)
        df = df.set_index('when')

        sheet = c
        if len(sheet) > 30:
            sheet.replace('-', '')        
        df.to_excel(w, sheet_name=sheet)
        w.save()
  
    print("...exposure sensitivity totals to file.")

    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')
    
    return net_CO2_dict