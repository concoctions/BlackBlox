
"""
Author: Ir. S.E. Tanzer
Affiliation: Delft Univeristy of Technology, Faculty of Technology, Policy, and
    Management
Date Created: 26 October 2020
Date Last Modified (code or data): 26 October 2020 

"""
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
from matplotlib.sankey import Sankey
import numpy as np


import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
sns.set_style("whitegrid", {'font':'Helvetica'})
from matplotlib.sankey import Sankey
import numpy as np

matplotlib.use('TkAgg')


def nh3_cases(product_name, factory_list, factory_names, f_suffix, f_kwargs, case_list):

    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')
    print(f'...generating cases{case_list} for {factory_names}')

    if product_name == 'NH3':
        product_label = 'NH$_3$'
    elif product_name == 'H2':
        product_label = 'H$_2$'
    else:
        product_label = product_name


    ## RUN all cases and get data
    ##---------------------------
    CO2_dict = nested_dicts(3) # CO2_dict[case][year][CO2_type]


    for i in range(len(factory_list)):

        multi_i, multi_o, multi_ai, multi_ao, multi_n =  factory_list[i].run_scenarios(case_list, **f_kwargs, write_to_xls=True
                                                                                    )

        # drop mass/energy index
        multi_i = multi_i.reset_index(level=0, drop=True)
        multi_o = multi_o.reset_index(level=0, drop=True)


    ## PRINT factory totals to console
    ##---------------------------------

        # print(factory_names[i])
        # print("\nIN FLOWS\n", multi_i)
        # print("\nOUT FLOWS\n", multi_o)
        # print("\nAGG IN FLOWS\n", multi_ai)
        # print("\nAGG OUT FLOWS\n", multi_ao)

        # print("\n\n")


    ## GET data for each case
    ##---------------------------------
        urea_as_product = False
        
        for j, c in enumerate(case_list):
            case = c+f_suffix[i]
            case = case.lower()
            c_new = ""
            if "bio" in case:
                if "pure" in case:
                    c_new += "BECCS, pure CO2"
                    c_label = " BECCS,\npure CO$_2$"
                elif "flue" in case:
                    c_new += "BECCS, flue CO2"
                    c_label = " BECCS,\nflue CO$_2$"
                elif "full" in case:
                    c_new += "BECCS, all CO2"
                    c_label = "BECCS,\nall CO$_2$"
                else:
                    c_new += "Biomass\nonly"
                    c_label = "Biomass\n     only"
            else:
                if "pure" in case:
                    c_new += "CCS,pure CO2"
                    c_label = "      CCS,\npure CO$_2$"
                elif "flue" in case:
                    c_new += "CCS,\nflue CO2"
                    c_label = " CS,nflue CO$_2$"
                elif "full" in case:
                    c_new += "CCS, all CO2"
                    c_label = "   CCS,\nall CO$_2$"
                else:
                    c_new += "Base case"
                    c_label = "Base\ncase"
            case = c_new
            
            CO2_dict[case]['meta']['subgraph x'] = j
            CO2_dict[case]['meta']['subgraph y'] = i
            CO2_dict[case]['meta']['filestring'] = c+f_suffix[i]
            CO2_dict[case]['meta']['label'] = c_label
            
            # get total flows
            CO2_dict[case]['totals']['CO2 emitted, total'] = multi_ao.loc['CO2', c]
            CO2_dict[case]['totals'][product_name] = multi_o.loc[product_name, c.lower()]
            CO2_dict[case]['totals']['CO2 removed, total'] = multi_o.loc['contrib - produced CO2__bio', c.lower()] 

            contrib_flows = [
                              ('CO2 produced, bio', 'contrib - produced CO2__bio'),
                              ('CO2 produced, fossil', 'contrib - produced CO2__fossil'),
                              ('CO2 emitted, fossil, of which electricity', 'contrib-electricity - CO2 fossil'),
                              ('CO2 emitted, fossil, of which electricity for CCS', 'contrib-electricity CCS - CO2 fossil'),
                              ('CO2 emitted, fossil, of which losses from urea synthesis', 'contrib - CO2 fossil losses Urea'),
                              ('CO2 emitted, bio, of which losses from urea synthesis', 'contrib - CO2 bio losses Urea'),
                              ('CO2 produced, bio, from H2 production', 'contrib - SMR feedstock CO2__bio'),
                              ('CO2 produced, fossil, from H2 production', 'contrib - SMR feedstock CO2__fossil'),
                              ('CO2 produced, bio, heat for H2 production', 'contrib - SMR fuel CO2__bio'),
                              ('CO2 produced, fossil, heat for H2 production', 'contrib - SMR fuel CO2__fossil'),
                              ('CO2 produced, bio, of which for heat', 'contrib heat - CO2 bio'),
                              ('CO2 produced, fossil, of which for heat', 'contrib heat - CO2 fossil'),
                              ]
            for k, f in contrib_flows:
                if f in multi_o.index:
                    CO2_dict[case][0][k] = multi_o.loc[f, c.lower()]

            # total electricity CO2
            CO2_dict[case][0]['CO2 emitted, fossil, of which electricity, total'] = CO2_dict[case][0]['CO2 emitted, fossil, of which electricity']  + CO2_dict[case][0]['CO2 emitted, fossil, of which electricity for CCS'] 

            contrib_agg_flows = [('CO2 emitted, upstream', 'CO2__upstream'),
                                 ('CO2 emitted, infrastructure', 'CO2 infrastructure'),
                                 ('CO2 emitted, fossil (total)', 'CO2__fossil'),
                                 ('CO2 emitted, biogenic (total)', 'CO2__bio'),
                                  ]

            for k, f in contrib_agg_flows:
                if f in multi_ao.index:
                    CO2_dict[case][0][k] = multi_ao.loc[f, c]

            contrib_inflows = [('maize (dry), in', 'maize (dry)'),
                               ]
            for k, f in contrib_inflows:
                if f in multi_i.index:
                    CO2_dict[case][0][k] = multi_i.loc[f, c.lower()]

            if 'CO2__released' in multi_o.index:
                if 'BIO' in c:
                    CO2_dict[case][0]['CO2 emitted, biogenic (total)'] +=  multi_o.loc['CO2__released', c.lower()] 
                else:
                    CO2_dict[case][0]['CO2 emitted, fossil (total)'] +=  multi_o.loc['CO2__released', c.lower()]

            # add CCS stored CO2 and produced CO2
            if 'stored CO2' in multi_o.index:
                CO2_dict[case]['meta']['CCS'] = True

                CO2_dict[case]['totals']['stored CO2'] += multi_o.loc['stored CO2', c.lower()]

                contrib_flows = [('CO2 emitted, fossil, of which heat for CCS', 'contrib heat CCS - CO2 fossil'),
                    ('CO2 emitted, biogenic, of which heat for CCS', 'contrib heat CCS - CO2 bio'),
                    ('CO2 emitted, upstream, of which transport', 'CO2__upstream (transport - pipeline onshore  (tkm))')]
                    
                for k, f in contrib_flows:
                    if f in multi_o.index:
                        CO2_dict[case][0][k] = multi_o.loc[f, c.lower()]

            # add CCS losses 
            if 'BIO' in c and 'CO2__lost - CCS' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, biogenic, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()] 
                CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += multi_o.loc['CO2__lost - CCS', c.lower()]

            elif 'CO2__lost - CCS' in multi_o.index:
                CO2_dict[case][0]['CO2 emitted, fossil, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()] 
                CO2_dict[case][0]['CO2 emitted, fossil (total)'] += multi_o.loc['CO2__lost - CCS', c.lower()]

            # add downstream emissions of CO2 from urea
            if 'Urea' in multi_o.index:
                urea_as_product = True
                urea = multi_o.loc['Urea', c.lower()] 
                urea_CO2 = urea * (12/60.056) * (44/12)
                CO2_dict[case]['totals']['CO2 emitted, total'] += urea_CO2
                CO2_dict[case][0]['CO2 emitted by urea'] = urea_CO2
                if 'BIO' in c: # note: CO2 removal embodied in Urea counted in NH3 proccess ('CO2__bio in syngas' which is also within the flow 'contrib - produced CO2__bio')
                    CO2_dict[case][0]['CO2 emitted, biogenic, of which urea'] = urea_CO2
                    CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += urea_CO2
                else:
                    CO2_dict[case][0]['CO2 emitted, fossil, of which urea'] = urea_CO2
                    CO2_dict[case][0]['CO2 emitted, fossil (total)'] += urea_CO2


            ## CALCULATE digestate emissions
            if 'digestate' in multi_o.index: 
                CO2_dict[case]['meta']['digestate'] = True
                C_in_biomass = multi_i.loc['food waste 50% H2O', c.lower()] * 0.27
                C_in_bioCH4 = (CO2_dict[case][0]['CO2 produced, bio, from H2 production'] + CO2_dict[case][0]['CO2 produced, bio, heat for H2 production']) * 12/44 + multi_o.loc['CH4__bio lost', c.lower()] * 12/16
                C_in_bioCH4_fuel = (CO2_dict[case][0]['CO2 produced, bio, of which for heat'] + CO2_dict[case][0]['CO2 emitted, biogenic, of which heat for CCS']) * 12/44
                C_in_biogas = (multi_o.loc['contrib - biogas lost CO2__bio', c.lower()] + multi_o.loc['contrib - bioCH4 CO2 pure__bio', c.lower()] +  multi_o.loc['contrib - bioCH4 lost CO2__bio', c.lower()]) * 12/44
                C_in_digestate = C_in_biomass - C_in_bioCH4 - C_in_biogas
                digestate_CO2 = C_in_digestate * (44/12)

                CO2_dict[case][0]['CO2 emitted, biogenic, of which digestate'] = digestate_CO2
                CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += digestate_CO2
                CO2_dict[case]['totals']['CO2 emitted, total'] += digestate_CO2
                CO2_dict[case]['totals']['CO2 removed, total'] += digestate_CO2

            for d in CO2_dict[case]:
                for k in CO2_dict[case][d]:
                    v = CO2_dict[case][d][k]
                    CO2_dict[case][d][k] = np.nan_to_num(v)


    print("...all cases run.")




    ## WRITE TO FILE Totals Data
    ##---------------------------

    # meta_dict = {'all cases': {
    #             'Biomass rotation period': r,
    #             }} 

    totals_dict = nested_dicts(2)
    gate_dict = nested_dicts(2)

    CO2_generated = []
    CO2_emitted = []
    CO2_removed = []

    for c in CO2_dict:
        totals_dict[c] = CO2_dict[c]['totals']
        totals_dict[c]['net CO2'] = (totals_dict[c]['CO2 emitted, total'] - totals_dict[c]['CO2 removed, total'])
        gate_dict[c] = CO2_dict[c][0]
        CO2_emitted.append(totals_dict[c]['CO2 emitted, total'])
        CO2_removed.append(totals_dict[c]['CO2 removed, total'])
        CO2_generated.append(totals_dict[c]['CO2 emitted, total'] + totals_dict[c]['stored CO2'])

    # meta_df = make_df(meta_dict).sort_index()
    totals_df = make_df(totals_dict).sort_index()
    gate_df = make_df(gate_dict).sort_index()

    if product_name is "NH3":
        alt_unit = "t N"
        unit_div = 14/17

    if product_name is "Urea":
        alt_unit = "t N"
        unit_div = 28/60

    if product_name is "H2":
        alt_unit = "GJ"
        unit_div = 120

    N_totals_dict = nested_dicts(2)

    N_CO2_generated = []
    N_CO2_emitted = []
    N_CO2_removed = []

    for c in CO2_dict:
        for k in CO2_dict[c]['totals']:
            N_totals_dict[c][k] = CO2_dict[c]['totals'][k] / (unit_div)
        N_totals_dict[c]['net CO2'] = (totals_dict[c]['CO2 emitted, total']  / (unit_div) - totals_dict[c]['CO2 removed, total']  / (unit_div)) 
        N_CO2_emitted.append(totals_dict[c]['CO2 emitted, total']  / (unit_div))
        N_CO2_removed.append(totals_dict[c]['CO2 removed, total']  / (unit_div))
        N_CO2_generated.append((totals_dict[c]['CO2 emitted, total'] + totals_dict[c]['stored CO2'])/ (unit_div))

    N_totals_df = make_df(N_totals_dict).sort_index()

    

    with ExcelWriter(f"{dat.path_outdir}/{product_name}_totalsOverTime_{dat.time_str}.xlsx") as writer:
        # meta_df.to_excel(writer, sheet_name='meta')
        totals_df.to_excel(writer, sheet_name='totals')
        gate_df.to_excel(writer, sheet_name='production')
        N_totals_df.to_excel(writer, sheet_name=f'per {alt_unit}')



    print("...totals data writ to file")


    ## GRAPH CO2 Contribution Chart
    ##---------------------------
    max_CO2 = round(max(CO2_generated)) * 1.0 + 1
    min_CO2 = round(max(CO2_removed)) * -1 

    # Where to save figures
    fig_path = f'{dat.path_outdir}/figures_base'
    Path(fig_path).mkdir(parents=True, exist_ok=True) 

    plt.rcParams["figure.figsize"] = (8,5)
    fig, ax = plt.subplots()

    labels = []
    CO2_upstream = []
    CO2_fossil = [] # fossil CO2 not from electricity (fuel combustion)
    CO2_elec = []
    CO2_bio = []
    CO2_urea = []
    CO2_residues = []
    CO2_stored = []
    CCS_fossil = []
    CCS_bio = []

    CO2_removed_feedstock = []
    CO2_removed_fuel = []
    CO2_removed_CCS = []

    net_CO2 = []


    # arrange data into lists
    for c in CO2_dict:
        d = CO2_dict[c]
        labels.append(d['meta']['label'])

        # CO2 emissions
        CO2_upstream.append((d[0]['CO2 emitted, upstream'] + d[0]['CO2 emitted, infrastructure']))
        CO2_fossil.append(d[0]['CO2 emitted, fossil (total)'] - d[0]['CO2 emitted, fossil, of which urea'] - d[0]['CO2 emitted, fossil, of which electricity, total'] - d[0]['CO2 emitted, fossil, of which heat for CCS'])
        CO2_elec.append(d[0]['CO2 emitted, fossil, of which electricity, total'] - d[0]['CO2 emitted, fossil, of which electricity for CCS'] )
        CCS_fossil.append(d[0]['CO2 emitted, fossil, of which electricity for CCS'] + d[0]['CO2 emitted, fossil, of which heat for CCS'])
        CCS_bio.append(d[0]['CO2 emitted, biogenic, of which heat for CCS'])
        CO2_residues.append(d[0]['CO2 emitted, biogenic, of which digestate'])
        CO2_bio.append((d[0]['CO2 emitted, biogenic (total)'] - d[0]['CO2 emitted, biogenic, of which digestate']) - d[0]['CO2 emitted, biogenic, of which urea'] - d[0]['CO2 emitted, biogenic, of which heat for CCS'])
        CO2_urea.append(d[0]['CO2 emitted by urea'])

        # CO2 removals
        CO2_removed_feedstock.append((d['totals']['CO2 removed, total'] - d[0]['CO2 produced, bio, heat for H2 production'] - d[0]['CO2 produced, bio, of which for heat'] - d[0]['CO2 emitted, biogenic, of which heat for CCS']) * -1)
        CO2_removed_fuel.append((d[0]['CO2 produced, bio, heat for H2 production'] + d[0]['CO2 produced, bio, of which for heat'])  * -1)
        CO2_removed_CCS.append(d[0]['CO2 emitted, biogenic, of which heat for CCS'] * -1)
        CO2_stored.append(d['totals']['stored CO2'] )

        # net CO2
        net_CO2.append((d['totals']['CO2 emitted, total'] - d['totals']['CO2 removed, total']) )


    if 'B' in c:
        label_product = f'{product_label} (and bioCH$_4$)'
    else:
        label_product = label_product

    # Add positive values
    if urea_as_product is True:
        data = np.array([CO2_fossil, CO2_elec, CCS_fossil,
                        CO2_bio, CCS_bio,
                        CO2_urea, CO2_residues,
                        CO2_upstream, CO2_stored
                        ])

        data = np.nan_to_num(data)

        bar_labels = [f"emitted, fossil,\n chemical production", f"emitted, fossil,\n electricity", "emitted, fossil,\n CCS heat and electricity", 
                f"emitted, biogenic,\n chemical (and bioCH$_4$) production", "emitted,\nCCS heat and electricity", 
                "emitted, biogenic,\n urea use", 'emitted, biogenic,\n digestate use', 
                "emitted, upstream", "stored geologically\n (i.e. generated but not emitted)"]
        color_list = ['#000b12', '#000b12', '#000b12',
                    '#45365d','#45365d', 
                    '#bd5170','#bd5170', 
                    '#ff9a42', 'none']
        edgecolor_list = ['white', 'none', 'none',
                        'white', 'none', 
                        'white', 'none', 
                        'white', '#ffd03d']
        width =[0.8, 0.8, 0.8,
                0.8, 0.8,
                0.8, 0.8, 
                0.8, 0.76]
        hatch = ['', '|||', '///',
                '', '///',
                '', '\\\\', 
                '', '///']

        hatch_color = [None, 'white', 'white',
                    None, 'white', 
                    None, 'white', 
                    None, '#ffd03d']

        linestyles = ['-', '-', '-', 
                    '-', '-',
                    '-', '-', 
                    '-', (0, (5, 5)) ]

    else:
        data = np.array([CO2_fossil, CO2_elec, CCS_fossil,
                        CO2_bio, CCS_bio,
                        CO2_residues,
                        CO2_upstream, CO2_stored
                        ])

        data = np.nan_to_num(data)

        bar_labels = [f"emitted, fossil,\n chemical production ", f"emitted, fossil,\n electricity", "emitted, fossil,\n CCS heat and electricity", 
                f"emitted, biogenic,\n chemical (and bioCH$_4$) production", "emitted biogenic,\n CCS heat", 
                'emitted, biogenic,\n digestate use', 
                "emitted, upstream", "stored geologically\n (i.e. generated but not emitted)"]        
        color_list = ['#000b12', '#000b12', '#000b12',
                    '#45365d','#45365d', 
                    '#bd5170',
                    '#ff9a42', 'none']
        edgecolor_list = ['white', 'none', 'none',
                        'white', 'none', 
                         'none', 
                        'white', '#ffd03d']
        width =[0.8, 0.8, 0.8,
                0.8, 0.8,
                0.8,
                0.8, 0.76]
        hatch = ['', '|||', '///',
                '', '///',
                '\\\\', 
                '', '///']

        hatch_color = [None, 'white', 'white',
                    None, 'white', 
                    'white', 
                    None, '#ffd03d']

        linestyles = ['-', '-', '-', 
                    '-', '-',
                     '-', 
                    '-', (0, (5, 5)) ]

    X = np.arange(data.shape[1])

    for i in reversed(range(data.shape[0])):
        ax.bar(X, data[i],
            width = width[i],
            bottom = np.sum(data[:i], axis = 0),
            color = color_list[i % len(color_list)],
            label = bar_labels[i],
            hatch = hatch[i],
            edgecolor = hatch_color[i],
            ls = linestyles[i]
            )
        
        ax.bar(X, data[i],
            width = width[i],
            bottom = np.sum(data[:i], axis = 0),
            color = 'none',
            edgecolor = edgecolor_list[i],
            ls = linestyles[i]
            )           

    # Add negative values

    data = np.array([
                    CO2_removed_feedstock,
                    CO2_removed_fuel,
                    CO2_removed_CCS
                    ])

    bar_labels = [f"removed from atmosphere,\n feedstock for {product_label}", f"removed from atmosphere,\n fuel", f"removed from atmosphere,\n fuel for CO$_2$ capture"]
    color_list = ['#007069', '#75d62b', '#75d62b']
    hatch = ['', '', '///']
    edgecolor_list = ['white', 'white', 'none']
    hatch_color = [None, None, 'white']

    # Add negative values
    for i in range(data.shape[0]):
        ax.bar(X, data[i],
            bottom = np.sum(data[:i], axis = 0),
            color = color_list[i % len(color_list)],
            label = bar_labels[i],
            hatch = hatch[i],
            edgecolor = hatch_color[i],
            )
        
        ax.bar(X, data[i],
            bottom = np.sum(data[:i], axis = 0),
            color = 'none',
            edgecolor = edgecolor_list[i]
            )       

    ax.axhline(0, color='#B2B2B2')
    ax.plot(net_CO2, linestyle="", marker="D", label="net CO$_2$\n(emissions minus removals)", color="#84ccf3", markeredgewidth=1.0, markeredgecolor='white')
 

    # add formatting
    if max_CO2 - min_CO2 > 40:
        min_minus = round(min_CO2,-1)
        if min_minus < min_CO2:
            min_CO2 = min_minus
        else:
            min_CO2 = round(min_CO2,-1)
        ytic = 10.0
    elif max_CO2 - min_CO2 > 20:
        if (min_CO2 % 2) != 0:
            min_CO2 = min_CO2 - 1
        ytic = 2.0
    else:
        ytic = 1.0

    ax.set_yticks(np.arange(min_CO2, max_CO2, ytic))
    ax.set_ylabel(f"t CO$_2$ per t {product_label}")
    idx = np.asarray([i for i in range(len(labels))])
    plt.xticks(ticks=idx, labels=labels, rotation=90, fontsize="10")

    # create secondary axis
    def unit2alt(x):
        return(x / (unit_div))

    def alt2unit(x):
        return(x * (unit_div))

    secaxy = ax.secondary_yaxis('right', functions=(unit2alt, alt2unit))
    secaxy.set_ylabel(f"t CO$_2$ per {alt_unit} in {product_label}", rotation=270, va='bottom')

    if product_name == 'H2':
        sec_tic = 0.05
        sec_min = -0.4
        sec_max = 0.46
    else:
        sec_tic = 1.0 
        sec_min = round(min_CO2/unit_div)
        sec_max = round(max_CO2/unit_div)
    print(unit_div, sec_min, sec_max, sec_tic)
    secaxy.set_yticks(np.arange(sec_min, sec_max, sec_tic))

    plt.legend(loc="upper right", fontsize="8.5", bbox_to_anchor=(1.8,1.02)) # bbox_to_anchor=(2.3,1.01))
    plt.subplots_adjust(left=0.08, right=0.58, bottom=0.2)

    fig.suptitle(f"Life Cycle CO$_2$ of {product_label}", x=0.33, fontsize='12', weight='bold')   

    # plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print('formatting added')


    # plt.show()
    plt.savefig(f'{fig_path}/{product_name}_Contribution.png', dpi=200)
    plt.close()

    print("...CO2 contributions graphs created.")


## GRAPH C-flow
    ##---------------------------
    for c in CO2_dict:
        d = CO2_dict[c]
        filestr = d['meta']['filestring']

        # c_in
        c_in = []
        c_in_labels = []
        c_in_or = []
        c_in_fossil = d[0]['CO2 produced, fossil'] *1000
        if round(c_in_fossil,3) == 0:
            c_in_fossil = 0
        c_in_bio = d['totals']['CO2 removed, total'] * 1000
        if round(c_in_bio,3) == 0:
            c_in_bio = 0
        if c_in_fossil != 0:
            c_in.append(c_in_fossil)
            c_in_labels.append('fossil')
            c_in_or.append(-1)
        if c_in_bio != 0:
            c_in.append(c_in_bio)
            c_in_labels.append('biogenic')
            c_in_or.append(1)
        c_in.append(sum(c_in) * -1)
        c_in_labels.append(None)
        c_in_or.append(0)

        c_production = -1000 * (d['totals']['CO2 emitted, total'] - d[0]['CO2 emitted, upstream'] - d[0]['CO2 emitted, infrastructure'] -  d[0]['CO2 emitted by urea'] - d[0]['CO2 emitted, biogenic, of which digestate'])
        c_product = -1000 * (d[0]['CO2 emitted, biogenic, of which digestate'] + d[0]['CO2 emitted by urea'])
        c_stored = -1000 * d['totals']['stored CO2']
        c_prod = [c_in[-1] * -1]
        c_prod.extend([c_production])
        c_prod_labels = ['', 'production']
        c_prod_or = [0, 1]

        if product_name is "Urea" or 'Bio' in c or 'BECCS' in c:
            c_prod.append(c_product)
            c_prod_labels.append(None)
            c_prod_or.append(0)
    
        if c_stored < 0:
            c_prod.append(c_stored)
            c_prod_labels.append('CCS')
            c_prod_or.append(-1)

        c_use = -1000 * d[0]['CO2 emitted by urea']
        c_residue =  -1000 * d[0]['CO2 emitted, biogenic, of which digestate']

        if product_name is "Urea" or 'Bio' in c or 'BECCS' in c:
            c_down = [c_prod[2] * -1]
            c_down_labels = ['']
            c_down_or =  [0]

            if c_use < 0:
                c_down.append(c_use)
                c_down_labels.append(product_name)
                c_down_or.append(1)

            if c_residue < 0:
                c_down.append(c_residue)
                c_down_labels.append('digestate')
                c_down_or.append(1)

        c_in_total =  c_in_fossil + c_in_bio
        c_out_total = -1*c_production + -1*c_stored + -1*c_residue + -1*c_use

        fig = plt.figure()
        plt.style.use('seaborn-colorblind')
        ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                            title=f"Carbon Flow of {product_label} - {c} \n kg CO2-equiv per t {product_label}")

        if  c_in_total > 20000:
            scale = 0.00001
        elif c_in_total > 5000:
            scale = 0.00005
        else:
            scale = 0.0001

        sankey = Sankey(ax=ax, scale=scale, offset=0.15, head_angle=90,
                        format='%.0f',)

        sankey.add(flows=c_in,
                labels=c_in_labels,
                orientations=c_in_or,
                label="Fuel & Feedstock",
                edgecolor = '#1d2f3d',
                facecolor = '#1d2f3d',)  
        sankey.add(flows=c_prod,
                labels=c_prod_labels,
                orientations=c_prod_or,
                label=f"{product_label} production",
                prior=0,
                connect=(len(c_in)-1, 0),
                edgecolor = '#7f4d87',
                facecolor = '#7f4d87',)
 
        if product_name is "Urea" or 'Bio' in c or 'BECCS' in c:
            sankey.add(flows=c_down,
                    labels=c_down_labels,
                    orientations=c_down_or,
                    label="end use",
                    prior=1,
                    connect=(2, 0),
                    edgecolor = '#ff6363',
                    facecolor = '#ff6363')

        diagrams = sankey.finish()

        # c-fossil in label
        xy = diagrams[0].texts[0].get_position()
        x_coord = xy[0]
        y_coord = xy[1] - 0.1
        xy = (x_coord, y_coord)
        diagrams[0].texts[0].set_position(xy)

        # c-bio in label
        xy = diagrams[0].texts[1].get_position()
        x_coord = xy[0]
        if 'Bio' in c or 'BECCS' in c:
            y_coord = xy[1] + 0.4
        else: 
            y_coord = xy[1] + 0.05
        xy = (x_coord, y_coord)
        diagrams[0].texts[1].set_position(xy)

       # c-in outflow label
        xy = diagrams[1].texts[0].get_position()
        x_coord = xy[0] - 0.2
        y_coord = xy[1] 
        xy = (x_coord, y_coord)
        diagrams[1].texts[0].set_position(xy)
        diagrams[1].texts[0].set_color('white')  

        if product_name is "Urea" or 'Bio' in c or 'BECCS' in c:
        # c-prod outflow label
            xy = diagrams[2].texts[0].get_position()
            x_coord = xy[0] - 0.2
            y_coord = xy[1] 
            xy = (x_coord, y_coord)
            diagrams[2].texts[0].set_position(xy)    
            diagrams[2].texts[0].set_color('white')  

            # c-product emissions label
            if len(diagrams[2].texts) > 1:
                xy = diagrams[2].texts[1].get_position()
                x_coord = xy[0]
                y_coord = xy[1] + 0.2
                xy = (x_coord, y_coord)
                diagrams[2].texts[1].set_position(xy)

        for diagram in diagrams:
            for text in diagram.texts:
                text.set_fontsize(8)

        c_in_total =  round(c_in_fossil + c_in_bio,0)
        c_out_total = round(-1*c_production + -1*c_stored + -1*c_residue + -1*c_use,0)

        x_sink = 0.3
        y_sink = 1.05
        if 'Bio' not in c and 'BECCS' not in c:
            y_sink = 0.75
        # if product_name is not 'NH3' and 'Bio' in c or 'BECCS' in c:
        #     sink_loc = 1.05
        # else:
        #     sink_loc = 1.2
        # if product_name is 'NH3':
        #     sink_loc -= 0.2
        # if product_name is 'H2':
        #     sink_loc -= 0.05
        x_box = 0.9
        y_box = -1.0
        if product_name is "Urea" or 'Bio' in c or 'BECCS' in c:
            x_sink = 0.6
            x_box = 1.6
            y_box = -1.2
        elif product_name is 'H2' and 'CCS' in c:
            y_sink += 0.2
            y_box = -1.2
        elif 'Base' in c:
            y_box = -0.8

        ax.text(x_sink, y_sink, 'Atmosphere', fontsize=10,  color='black', style='italic',)
        ax.text(x_sink, y_sink * -1, 'Geologic Sink', fontsize=10,  color='black', style='italic',)
        plt.legend(loc='lower left', fontsize=8)
        ax.text(x_box, y_box, f'  CO2 in: {int(c_in_total)}\nCO2 out: {int(c_out_total)}', fontsize=8,  color='black', bbox=dict(facecolor='none', edgecolor='grey', pad=5.0))
        plt.box(on=None)

        if c_in_total - c_out_total != 0:
            print("ERROR!")
            print(f"C in ({c_in_total}) does not equal C out ({c_out_total}) for {c}.\nDiff (in-out) = {c_in_total - c_out_total}")

        plt.savefig(f'{fig_path}/{product_name}_{filestr}_sankey.png')
        plt.close()


    print("...sankey graphs created.")



    # PRNT totals to console
    #---------------------------
    # for c in CO2_dict:

    #     print(f"\n{c}, TOTALS")
    #     [print ("  ",k,v) for k,v, in CO2_dict[c]['totals'].items()]
    #     print("\n")

    #     print(f"\n{c}, GATE-TO-GATE")
    #     [print ("  ",k,v) for k,v, in CO2_dict[c][0].items()]
    #     print("\n")

    #     print(f"\n{c}, DEMO")
    #     [print ("  ",k,v) for k,v, in CO2_dict[c][concrete_life+1].items()]
    #     print("\n")

    #     for y in CO2_dict[c]:
    #         if y != 'totals':
    #             print(f"\n{c}, year {y}")
    #             [print ("  ",k,v) for k,v, in CO2_dict[c][y].items()]
    #         print("\n")

    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')

    return(CO2_dict)

    
