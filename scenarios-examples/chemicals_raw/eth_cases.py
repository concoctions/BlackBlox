
"""
Author: Ir. S.E. Tanzer
Affiliation: Delft Univeristy of Technology, Faculty of Technology, Policy, and
    Management
Date Created: 26 October 2020
Date Last Modified (code or data): 26 October 2020 

"""
from pathlib import Path
from datetime import datetime
from pandas import ExcelWriter
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
import numpy as np
import seaborn as sns

import blackblox.dataconfig as dat
from blackblox.io_functions import make_df
from blackblox.io_functions import nested_dicts

sns.set_style("whitegrid", {'font': 'Helvetica'})
matplotlib.use('TkAgg')


def eth_cases(product_name, factory_list, factory_names, f_suffix, f_kwargs, case_list, feedstock='', fuel=''):
    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')
    print(f'...generating cases{case_list} for {factory_names}')
    print(dat.time_str)

    # RUN all cases and get data
    CO2_dict = nested_dicts(3)  # CO2_dict[case][year][CO2_type]
    product = product_name

    for i in range(len(factory_list)):
        multi_i, multi_o, multi_ai, multi_ao, multi_n = factory_list[i].run_scenarios(
            case_list, **f_kwargs, write_to_xls=True
        )
        # drop mass/energy index
        multi_i = multi_i.reset_index(level=0, drop=True)
        multi_o = multi_o.reset_index(level=0, drop=True)

        # PRINT factory totals to console
        # print(factory_names[i])
        # print("\nIN FLOWS\n", multi_i)
        # print("\nOUT FLOWS\n", multi_o)
        # print("\nAGG IN FLOWS\n", multi_ai)
        # print("\nAGG OUT FLOWS\n", multi_ao)

        # print("\n\n")

        # GET data for each case
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
            if 'lignin' in case:
                c_new += 'lignin energy for CCS'
            case = c_new

            CO2_dict[case]['meta']['subgraph x'] = j
            CO2_dict[case]['meta']['subgraph y'] = i
            CO2_dict[case]['meta']['label'] = c_label
            CO2_dict[case]['meta']['filestring'] = c+f_suffix[i]

            # get total flows
            CO2_dict[case]['totals']['CO2 emitted, total'] = multi_ao.loc['CO2', c]
            CO2_dict[case]['totals']['C2H6O'] = multi_o.loc['C2H6O', c.lower()]
            # CO2 produced at ethanol factory (from fermentation and steam generation)
            CO2_dict[case]['totals']['CO2 removed, total'] = multi_o.loc['contrib - produced CO2__bio', c.lower()]

            contrib_flows = [
                ('CO2 emitted, biogenic (total)', 'CO2__bio'),
                ('CO2 emitted, fossil (total)', 'CO2__fossil'),
                ('CO2 emitted, fossil, of which electricity', 'contrib-electricity - CO2 fossil'),
                ('CO2 emitted, fossil, of which electricity for CCS', 'contrib-electricity CCS - CO2 fossil'),
                ('CO2 produced, bio, of which ethanol', 'contrib - ethanol CO2__bio'),
                ('CO2 produced, fossil', 'contrib - produced CO2__fossil'),
                ('CO2 produced, bio', 'contrib - produced CO2__bio'),
                ('CO2 produced, bio, of which heat', 'contrib heat - CO2 bio'),
                ('CO2 produced, fossil, of which heat', 'contrib heat - CO2 fossil'),
                ('CO2 produced, bio, of which heat from lignin', 'contrib heat aux - CO2 bio '),
            ]
            for k, f in contrib_flows:
                if f in multi_o.index:
                    CO2_dict[case][0][k] = multi_o.loc[f, c.lower()]

            # total electricity CO2
            CO2_dict[case][0]['CO2 emitted, fossil, of which electricity, total'] =\
                CO2_dict[case][0]['CO2 emitted, fossil, of which electricity']\
                + CO2_dict[case][0]['CO2 emitted, fossil, of which electricity for CCS']

            contrib_agg_flows = [
                ('CO2 emitted, upstream', 'CO2__upstream'),
                ('CO2 emitted, infrastructure', 'CO2 infrastructure'),
            ]
            for k, f in contrib_agg_flows:
                if f in multi_ao.index:
                    CO2_dict[case][0][k] = multi_ao.loc[f, c]

            contrib_inflows = [
                ('maize (dry), in', 'maize (dry)'),
                ('maize (dry), in', 'maize (dry) - Swiss'),
                ('maize (dry), in', 'maize (dry) - Brazil'),
                ('maize (dry), in', 'maize (dry) - Organic'),
                ('maize (dry), in', 'maize (dry) - ROW'),
            ]
            for k, f in contrib_inflows:
                if f in multi_i.index:
                    CO2_dict[case][0][k] = multi_i.loc[f, c.lower()]

            # CO2_dict[case][0]['CO2 emitted, upstream, of which transport'] =\
            #     multi_o.loc['CO2__upstream (transport - lorry (tkm))', c.lower()]\
            #     + multi_o.loc['CO2__upstream (transport - rail (tkm))', c.lower()]

            if 'stored CO2' in multi_o.index:
                CO2_dict[case]['meta']['CCS'] = True

                CO2_dict[case]['totals']['stored CO2'] = multi_o.loc['stored CO2', c.lower()]

                contrib_flows = [
                    ('CO2 emitted, fossil, of which heat for CCS', 'contrib heat CCS - CO2 fossil'),
                    ('CO2 emitted, biogenic, of which heat for CCS', 'contrib heat CCS - CO2 bio'),
                    ('CO2 emitted, upstream, of which transport', 'CO2__upstream (transport - pipeline onshore  (tkm))'),
                ]

                for k, f in contrib_flows:
                    if f in multi_o.index:
                        CO2_dict[case][0][k] = multi_o.loc[f, c.lower()]

                # breakdown of CO2 to capture by CO2 type
                CO2_dict[case][0]['CO2 to capture, biogenic'] = multi_o.loc['contrib - ethanol CO2__bio', c.lower()] + multi_o.loc['stored CO2', c.lower()]

                if 'BIO' in c:  # all emissions captured at ethanol plant are biogenic
                    CO2_dict[case][0]['CO2 emitted, biogenic, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()]
                    CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += multi_o.loc['CO2__lost - CCS', c.lower()]

                else:  # emissions from fermentation are biogenic, emissions from steam generation are not
                    total_CCS_CO2 = multi_o.loc['stored CO2', c.lower()] + multi_o.loc['CO2__lost - CCS', c.lower()]
                    CO2_dict[case][0]['CO2 to capture, biogenic'] = multi_o.loc['contrib - ethanol CO2__bio', c.lower()]
                    CO2_dict[case][0]['CO2 emitted, biogenic, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()] * (multi_o.loc['contrib - ethanol CO2__bio', c.lower()]/total_CCS_CO2)
                    CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += CO2_dict[case][0]['CO2 emitted, biogenic, of which CCS loss']

                    CO2_dict[case][0]['CO2 emitted, fossil, of which CCS loss'] = multi_o.loc['CO2__lost - CCS', c.lower()] * (1 - (multi_o.loc['contrib - ethanol CO2__bio', c.lower()]/total_CCS_CO2))
                    CO2_dict[case][0]['CO2 emitted, fossil (total)'] += CO2_dict[case][0]['CO2 emitted, fossil, of which CCS loss']

            # CALCULATE ethanol emissions
            C_in_eth = CO2_dict[case]['totals']['C2H6O'] * (24/(24+6+16))
            eth_CO2 = C_in_eth * (44/12)

            CO2_dict[case][0]['CO2 emitted, biogenic, of which ethanol combuston'] = eth_CO2
            CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += eth_CO2
            CO2_dict[case]['totals']['CO2 emitted, total'] += eth_CO2
            CO2_dict[case]['totals']['CO2 removed, total'] += eth_CO2

            # CALCULATE digestate emissions
            if 'digestate' in multi_o.index:  # digestate qty is the biomass qty that is not converted to ethanol or CO2
                CO2_dict[case]['meta']['digestate'] = True
                C_in_biomass = CO2_dict[case][0]['maize (dry), in'] * 0.45
                C_in_CO2 = CO2_dict[case][0]['CO2 produced, bio, of which ethanol'] * (12/44)
                C_in_digestate = C_in_biomass - C_in_eth - C_in_CO2
                digestate_CO2 = C_in_digestate * (44/12)

                CO2_dict[case][0]['CO2 emitted, biogenic, of which digestate'] = digestate_CO2
                CO2_dict[case][0]['CO2 emitted, biogenic (total)'] += digestate_CO2
                CO2_dict[case]['totals']['CO2 emitted, total'] += digestate_CO2
                CO2_dict[case]['totals']['CO2 removed, total'] += digestate_CO2

            if 'contrib heat aux - CO2 bio' in multi_o.index:
                CO2_dict[case]['meta']['lignin'] = True

    print("...all cases run.")

    # WRITE TO FILE Totals Data

    # meta_dict = {'all cases': {
    #             'Biomass rotation period': r,
    #             }} 

    product_filestr = 'ethanol-' + ('stover' if 'stover' in product_name else 'maize')

    totals_dict = nested_dicts(2)
    gate_dict = nested_dicts(2)
    GJ_totals_dict = nested_dicts(2)

    CO2_generated = []
    CO2_emitted = []
    CO2_removed = []
    GJ_CO2_generated = []
    GJ_CO2_emitted = []
    GJ_CO2_removed = []

    for c in CO2_dict:
        totals_dict[c] = CO2_dict[c]['totals']
        totals_dict[c]['net CO2'] = (totals_dict[c]['CO2 emitted, total'] - totals_dict[c]['CO2 removed, total'])
        gate_dict[c] = CO2_dict[c][0]
        CO2_emitted.append(totals_dict[c]['CO2 emitted, total'])
        CO2_removed.append(totals_dict[c]['CO2 removed, total'])
        CO2_generated.append(totals_dict[c]['CO2 emitted, total'] + totals_dict[c]['stored CO2'])

        for k in CO2_dict[c]['totals']:
            GJ_totals_dict[c][k] = CO2_dict[c]['totals'][k] / 26.7
        GJ_totals_dict[c]['net CO2'] = (totals_dict[c]['CO2 emitted, total'] / 26.7 - totals_dict[c]['CO2 removed, total'] / 26.7)
        GJ_CO2_emitted.append(totals_dict[c]['CO2 emitted, total'] / 26.7)
        GJ_CO2_removed.append(totals_dict[c]['CO2 removed, total'] / 26.7)
        GJ_CO2_generated.append((totals_dict[c]['CO2 emitted, total'] + totals_dict[c]['stored CO2']) / 26.7)

    totals_df = make_df(totals_dict).sort_index()
    gate_df = make_df(gate_dict).sort_index()
    GJ_totals_df = make_df(GJ_totals_dict).sort_index()

    with ExcelWriter(f"{dat.path_outdir}/{product_filestr}_totalsOverTime_{dat.time_str}.xlsx") as writer:
        totals_df.to_excel(writer, sheet_name='totals')
        gate_df.to_excel(writer, sheet_name='production')
        GJ_totals_df.to_excel(writer, sheet_name='per GJ')

    print("...totals data writ to file")

    # GRAPH CO2 Contribution Chart
    max_CO2 = round(max(CO2_generated)) * 1.0 + 1.1
    min_CO2 = round(max(CO2_removed)) * -1 - 1

    # Where to save figures
    fig_path = f'{dat.path_outdir}/figures_base'
    Path(fig_path).mkdir(parents=True, exist_ok=True)

    plt.rcParams["figure.figsize"] = (8, 5)
    fig, ax = plt.subplots()

    labels = []
    CO2_upstream = []
    CO2_fossil = []
    CO2_elec = []
    CO2_bio = []
    CO2_ethanol = []
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
        CO2_fossil.append(d[0]['CO2 emitted, fossil (total)'] - (d[0]['CO2 emitted, fossil, of which electricity, total'] + d[0]['CO2 emitted, fossil, of which heat for CCS']))
        CO2_elec.append(d[0]['CO2 emitted, fossil, of which electricity, total'] - d[0]['CO2 emitted, fossil, of which electricity for CCS'])
        CCS_fossil.append(d[0]['CO2 emitted, fossil, of which electricity for CCS'] + d[0]['CO2 emitted, fossil, of which heat for CCS'])
        CO2_bio.append(d[0]['CO2 emitted, biogenic (total)'] - d[0]['CO2 emitted, biogenic, of which digestate'] - d[0]['CO2 emitted, biogenic, of which ethanol combuston']-d[0]['CO2 emitted, biogenic, of which heat for CCS'])
        CCS_bio.append(d[0]['CO2 emitted, biogenic, of which heat for CCS'])
        CO2_ethanol.append(d[0]['CO2 emitted, biogenic, of which ethanol combuston'])

        if d['meta']['lignin'] is True and d['meta']['digestate'] is True:
            raise ValueError('digestate and lignin should not appear in the same system')

        elif d['meta']['lignin'] is True:
            if d['meta']['CCS'] is False:
                CO2_residues.append(d[0]['CO2 produced, bio, of which heat from lignin'])
            else:
                CO2_residues.append(0)

        elif d['meta']['digestate'] is True:
            CO2_residues.append(d[0]['CO2 emitted, biogenic, of which digestate'])

        else:
            CO2_residues.append(0)

        # CO2 removals
        CO2_removed_feedstock.append(
            -1 *
            (d['totals']['CO2 removed, total']
             - d[0]['CO2 produced, bio, of which heat']
             - d[0]['CO2 emitted, biogenic, of which heat for CCS'])
        )
        CO2_removed_fuel.append(d[0]['CO2 produced, bio, of which heat'] * -1)
        CO2_removed_CCS.append(d[0]['CO2 emitted, biogenic, of which heat for CCS'] * -1)

        CO2_stored.append(d['totals']['stored CO2'])

        # net CO2
        net_CO2.append((d['totals']['CO2 emitted, total'] - d['totals']['CO2 removed, total']))

    # Add positive values
    data = np.array([
        CO2_fossil, CO2_elec, CCS_fossil,
        CO2_bio, CCS_bio,
        CO2_ethanol, CO2_residues,
        CO2_upstream, CO2_stored,
    ])

    bar_labels = [
        "emitted, fossil,\n ethanol production", "emitted, fossil,\n electricity, ethanol production", "emitted, fossil,\n CCS heat and electricity",
        "emitted, biogenic,\n ethanol production", "emitted biogenic,\n CCS heat",
        "emitted, biogenic,\n ethanol use", 'emitted, biogenic,\n distiller grains use',
        "emitted, upstream", "stored geologically\n (i.e. generated but not emitted)",
    ]

    color_list = ['#000b12', '#000b12', '#000b12', '#45365d', '#45365d', '#bd5170', '#bd5170', '#ff9a42', 'none']
    edgecolor_list = ['white', 'none', 'none', 'white', 'none', 'white', 'none', 'white', '#ffd03d']
    width = [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.76]

    hatch = ['', '|||', '///', '', '///', '', '\\\\', '', '///']
    hatch_color = [None, 'white', 'white', None, 'white', None, 'white', None, '#ffd03d']

    linestyles = ['-', '-', '-', '-', '-', '-', '-', '-', (0, (5, 5))]

    X = np.arange(data.shape[1])

    for i in reversed(range(data.shape[0])):
        ax.bar(
            X, data[i],
            width=width[i],
            bottom=np.sum(data[:i], axis=0),
            color=color_list[i % len(color_list)],
            edgecolor=hatch_color[i],
            ls=linestyles[i],
            label=bar_labels[i],
            hatch=hatch[i],
        )

        ax.bar(
            X, data[i],
            width=width[i],
            bottom=np.sum(data[:i], axis=0),
            color='none',
            edgecolor=edgecolor_list[i],
            ls=linestyles[i],
        )

    data = np.array([
                    CO2_removed_feedstock,
                    CO2_removed_fuel,
                    CO2_removed_CCS
                    ])

    bar_labels = [f"removed from atmosphere,\n in feedstock", f"removed from atmosphere,\n in fuel ({fuel})", f"removed from atmosphere,\n in fuel ({fuel}), for CO$_2$ capture"]
    color_list = ['#007069', '#75d62b', '#75d62b']
    hatch = ['', '', '///']
    edgecolor_list = ['white', 'white', 'none']
    hatch_color = [None, None, 'white']

    # Add negative values
    for i in range(data.shape[0]):
        ax.bar(
            X, data[i],
            bottom=np.sum(data[:i], axis=0),
            color=color_list[i % len(color_list)],
            label=bar_labels[i],
            hatch=hatch[i],
            edgecolor=hatch_color[i],
        )

        ax.bar(
            X, data[i],
            bottom=np.sum(data[:i], axis=0),
            color='none',
            edgecolor=edgecolor_list[i],
        )

    ax.plot(net_CO2, linestyle="", marker="D", label="net CO$_2$\n(emissions minus removals)", color="#84ccf3", markeredgewidth=1.0, markeredgecolor='white')

    # add formatting
    ax.set_yticks(np.arange(min_CO2, max_CO2, 1.0))
    ax.set_ylabel(f"t CO$_2$ per t {product}")
    idx = np.asarray([i for i in range(len(labels))])
    plt.xticks(ticks=idx, labels=labels, rotation=90, fontsize="10")

    def t_to_GJ(x):
        return x / 27

    def GJ_to_t(x):
        return x * 27

    secaxy = ax.secondary_yaxis('right', functions=(t_to_GJ, GJ_to_t))
    secaxy.set_ylabel(f"t CO$_2$ per GJ {product_name}", rotation=270, va='bottom')

    if 'stover' in product_name:
        secaxy.set_yticks(np.arange(-0.3, 0.31, 0.05))
    else:
        secaxy.set_yticks(np.arange(round(min_CO2/27, 1), round(max_CO2/27, 1)+0.01, 0.05))
    plt.legend(loc="upper right", fontsize="8.5", bbox_to_anchor=(1.8, 1.02))  # bbox_to_anchor=(2.3,1.01))
    plt.subplots_adjust(left=0.08, right=0.58, bottom=0.2)

    fig.suptitle(f"Life Cycle CO$_2$ of Bioethanol from {feedstock}", x=0.33, fontsize='12', weight='bold')

    # plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print('formatting added')

    plt.savefig(f'{fig_path}/{product_filestr}_Contribution.png', dpi=200)
    plt.close()

    print("...CO2 contributions graphs created.")

    # GRAPH C-flow in sankey diagram
    for c in CO2_dict:
        d = CO2_dict[c]
        filestr = d['meta']['filestring']

        # c_in
        c_in = []
        c_in_labels = []
        c_in_or = []
        c_in_fossil = d[0]['CO2 produced, fossil'] * 1000
        if round(c_in_fossil, 3) == 0:
            c_in_fossil = 0
        c_in_bio = d['totals']['CO2 removed, total'] * 1000
        if round(c_in_bio, 3) == 0:
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

        c_production = -1000 * (d['totals']['CO2 emitted, total'] - d[0]['CO2 emitted, upstream'] - d[0]['CO2 emitted, infrastructure'] - d[0]['CO2 emitted, biogenic, of which ethanol combuston'] - d[0]['CO2 emitted, biogenic, of which digestate'])
        c_product = -1000 * (d[0]['CO2 emitted, biogenic, of which digestate'] + d[0]['CO2 emitted, biogenic, of which ethanol combuston'])
        c_stored = -1000 * d['totals']['stored CO2']
        c_prod = [c_in[-1] * -1]
        c_prod.extend([c_production, c_product])
        c_prod_labels = ['', 'production', None]
        c_prod_or = [0, 1, 0]

        if c_stored < 0:
            c_prod.append(c_stored)
            c_prod_labels.append('CCS')
            c_prod_or.append(-1)

        c_use = -1000 * d[0]['CO2 emitted, biogenic, of which ethanol combuston']
        c_residue = -1000 * d[0]['CO2 emitted, biogenic, of which digestate']
        c_down = [c_prod[2] * -1]

        if c_residue < 0:
            c_down.extend([c_use, c_residue])
            c_down_labels = ['', product_name, 'digestate']
            c_down_or = [0, 1, 1]
        else:
            c_down.extend([c_use])
            c_down_labels = ['', product_name]
            c_down_or = [0, 1]

        fig = plt.figure()
        plt.style.use('seaborn-colorblind')
        ax = fig.add_subplot(
            1, 1, 1, xticks=[], yticks=[],
            title=f"Carbon Flow of {product_name} - {c} \n kg CO2-equiv per t {product_name}",
        )
        sankey = Sankey(ax=ax, scale=0.0001, offset=0.15, head_angle=90, format='%.0f')

        # Arguments to matplotlib.patches.PathPatch()
        sankey.add(
            flows=c_in, labels=c_in_labels, orientations=c_in_or,
            label="Fuel & Feedstock", edgecolor='#1d2f3d', facecolor='#1d2f3d',
        )
        sankey.add(
            flows=c_prod, labels=c_prod_labels, orientations=c_prod_or,
            prior=0, connect=(len(c_in)-1, 0),
            label=f"{product_name} production", edgecolor='#7f4d87', facecolor='#7f4d87',
        )
        sankey.add(
            flows=c_down, labels=c_down_labels, orientations=c_down_or,
            prior=1, connect=(2, 0),
            label="end use", edgecolor='#ff6363', facecolor='#ff6363',
        )
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
        y_coord = xy[1] + 0.3
        if 'stover' in c and 'CCS' not in c:
            y_coord += 0.3
        xy = (x_coord, y_coord)
        diagrams[0].texts[1].set_position(xy)

        # c-in outflow label
        xy = diagrams[1].texts[0].get_position()
        x_coord = xy[0] - 0.2
        y_coord = xy[1]
        xy = (x_coord, y_coord)
        diagrams[1].texts[0].set_position(xy)
        diagrams[1].texts[0].set_color('white')

        # c-prod outflow label
        xy = diagrams[2].texts[0].get_position()
        x_coord = xy[0] - 0.2
        y_coord = xy[1]
        xy = (x_coord, y_coord)
        diagrams[2].texts[0].set_position(xy)
        diagrams[2].texts[0].set_color('white')

        # c-product emissions label
        xy = diagrams[2].texts[1].get_position()
        x_coord = xy[0]
        y_coord = xy[1] + 0.2
        xy = (x_coord, y_coord)
        diagrams[2].texts[1].set_position(xy)

        for diagram in diagrams:
            for text in diagram.texts:
                text.set_fontsize(8)

        c_in_total = c_in_fossil + c_in_bio
        c_out_total = (-1 * c_production) + (-1 * c_stored) + (-1 * c_residue) + (-1 * c_use)

        ax.text(0.75, 1.2, 'Atmosphere', fontsize=10,  color='black', style='italic',)
        ax.text(0.75, -1.2, 'Geologic Sink', fontsize=10,  color='black', style='italic',)
        ax.text(1.8, -1.3, f'  CO2 in: {int(c_in_total)}\nCO2 out: {int(c_out_total)}', fontsize=8,  color='black', bbox=dict(facecolor='none', edgecolor='grey', pad=5.0))

        plt.legend(loc='lower left', fontsize=8)
        plt.box(on=None)

        if round((c_in_total - c_out_total), -3) > 0:
            print("ERROR!")
            print(f"C in ({c_in_total}) does not equal C out ({c_out_total}) for {c}")

        plt.savefig(f'{fig_path}/{product_filestr}_{filestr}_sankey.png')
        plt.close()

    print("...sankey graphs created.")

    # PRINT totals to console
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

    return CO2_dict
