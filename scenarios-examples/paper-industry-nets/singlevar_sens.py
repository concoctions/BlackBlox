from pathlib import Path

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


## RUN sensitivities
##---------------------------




def multi_sens(product, factory_list, case_list, sdict=None):
    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')

    Path(f'{dat.path_outdir}/figures_sens/').mkdir(parents=True, exist_ok=True)

    if not sdict:
        sdict = nested_dicts(2)

    sdict['electricity']['variable'] = 'fueltype'
    sdict['electricity']['options'] = ['electricity 0g/kWh', 'electricity 200g/kWh', 'electricity 400g/kWh', 'electricity 600g/kWh', 'electricity 800g/kWh', 'electricity 1000g/kWh',]
    sdict['electricity']['chain'] = 'power'
    sdict['electricity']['unit'] = 'simple_power'
    sdict['electricity']['chain_CCS'] = ['power', 'CCS-power']
    sdict['electricity']['unit_CCS'] = ['simple_power', 'CCS_power']
    sdict['electricity']['fixed vars'] = [('combustion eff', 1.0)],
    sdict['electricity']['xticks'] = [0, 200, 400, 600, 800, 1000]
    sdict['electricity']['xlabel'] =  "g CO2/kWh"
    sdict['electricity']['title'] = "net CO2, by electricity CO2 intensity"
    sdict['electricity']['vline-loc'] = 1.8
    sdict['electricity']['vline-label'] = "natural gas"

    if 'maize' in product.lower():
        sdict['maize']['variable'] = 'biomass type'
        sdict['maize']['options'] = ['maize (dry) - Brazil', 'maize (dry) - Swiss', 'maize (dry) - Organic', 'maize (dry) - ROW']
        sdict['maize']['chain'] = 'ethanol'
        sdict['maize']['unit'] = 'eth_box'
        sdict['maize']['chain_CCS'] = 'ethanol'
        sdict['maize']['unit_CCS'] = 'eth_box'
        sdict['maize']['xticks'] = ['Brazil', 'Swiss', 'Global mix,\nOrganic', 'Global mix']
        sdict['maize']['xlabel'] =  "CO2 origin"
        sdict['maize']['title'] = "net CO2, by maize origin"
        sdict['maize']['vline-loc'] = 1
        sdict['maize']['vline-label'] = ""
        sdict['maize']['markers only'] = True
    else:
        if 'maize' in sdict:
            sdict.pop('maize')

    for s in sdict:

        print(f'...starting sensitivity analysis: {s} ({product})')        

        sens_dict = nested_dicts(2) # [case][df]

        for f in factory_list:

            for case in case_list:

                dict_case = f'{f.name}_{case}'
                
                in_df, out_df, agg_in_df, agg_out_df, net_df  = f.run_sensitivity(product_qty=1.0, 
                                scenario=case, 
                                chain_name=sdict[s]['chain'], 
                                unit_name=sdict[s]['unit'], 
                                variable=sdict[s]['variable'],
                                variable_options=sdict[s]['options'],
                                fixed_vars= sdict[s]['fixed vars'],
                                upstream_outflows=['CO2', 'CO2 infrastructure'],
                                upstream_inflows=['CO2 removed',],
                                aggregate_flows=['CO2', 'CO2__upstream', 'CO2 infrastructure']
                                )


                out_df = out_df.reset_index(level=0, drop=True)
                out_df.columns = sdict[s]['options']

                in_df = in_df.reset_index(level=0, drop=True)
                in_df.columns = sdict[s]['options']


                sens_dict[dict_case]['in'] = in_df
                sens_dict[dict_case]['out'] = out_df
                sens_dict[dict_case]['agg_out'] = agg_out_df
                sens_dict[dict_case]['agg_in'] = agg_in_df
                    

                if "BIO" in dict_case:
                    sens_dict[dict_case]['color'] = '#00b2b7'
                else:
                    sens_dict[dict_case]['color'] = '#250036'

                if "CCS" in dict_case:
                    sens_dict[dict_case]['linestyle'] = 'dotted'
                    sens_dict[dict_case]['marker'] = 'D'
                elif "pure" in dict_case:
                    sens_dict[dict_case]['linestyle'] = 'dashed'
                    sens_dict[dict_case]['marker'] = '^'
                else: 
                    sens_dict[dict_case]['linestyle'] = 'solid'
                    sens_dict[dict_case]['marker'] = 'o'

                    

        plt.figure()
        plt.style.context('seaborn')

        # case_order = ['BASE', '03AC', '10AC','CCS - BASE', 
        #             'CCS - 03AC', 'CCS - 10AC', 
        #             'BASE-BIO', '03AC-BIO', '10AC-BIO',
        #             'CCS - BASE-BIO', 'CCS - 03AC-BIO', 'CCS - 10AC-BIO']

        # case_names = ['Base', '0.3% AC', '10% AC',
        #             'CCS', 'CCS with 0.3% AC', 'CCS with 10% AC', 
        #             'Bioenergy',  'Bioenergy with 0.3% AC', 'Bioenergy with 10% AC',
        #             'BECCS', 'BECCS with 0.3% AC', 'BECCS with 10% AC']

        for c in sens_dict: #for n, c in enumerate(case_order):
            CO2_out = list(sens_dict[c]['agg_out'].loc['CO2' , :])
            downstream_CO2 = [0 for i in CO2_out]
            CO2_in = [0 for i in CO2_out]

            if 'CO2__bio' in sens_dict[c]['out'].index:
                CO2_in = list(sens_dict[c]['out'].loc['contrib - produced CO2__bio' , :])

            if 'C2H6O' in  sens_dict[c]['out'].index: 
                eth_out =  list(sens_dict[c]['out'].loc['C2H6O' , :])
                eth_CO2 = [i * (24/(24+6+16)) * (44/12) for i in eth_out]
                for i in range(len(downstream_CO2)):
                    downstream_CO2[i] += eth_CO2[i]
                    CO2_in[i] += eth_CO2[i]

                if 'digestate' in sens_dict[c]['out'].index:
                    for flow in sens_dict[c]['in'].index:
                        if flow.startswith('maize (dry)'):
                            feedstock = list(sens_dict[c]['in'].loc[flow, :])
                    feedstock_CO2 = [i * 0.45 * 44/12 for i in feedstock]    
                    ferment_CO2 = list(sens_dict[c]['out'].loc['contrib - ethanol CO2__bio' , :])
                    digestate_CO2 = []
                    for i in range(len(feedstock_CO2)):
                        digestate_CO2.append(feedstock_CO2[i] - eth_CO2[i] - ferment_CO2[i])

                    for i in range(len(downstream_CO2)):
                        downstream_CO2[i] += digestate_CO2[i]
                        CO2_in[i] += digestate_CO2[i]




            net_CO2 = [(CO2_out[i] + downstream_CO2[i] - CO2_in[i]) * 1000 for i in range(len(CO2_out))]

            if sdict[s]['markers only'] is True:
                plt.plot(net_CO2, label=c, linestyle='', marker=sens_dict[c]['marker'], color=sens_dict[c]['color'])
            else:
                plt.plot(net_CO2, label=c, linestyle=sens_dict[c]['linestyle'], color=sens_dict[c]['color'])

        idx = np.asarray([i for i in range(len(sdict[s]['options']))])
        plt.xticks(ticks=idx, labels=sdict[s]['xticks'], rotation=65, fontsize="8")
        plt.ylabel(f"kg CO2 per t {product}")
        plt.xlabel(sdict[s]['xlabel'])
        plt.title(sdict[s]['title'])
        plt.axvline(x=sdict[s]['vline-loc'], color='black', label=sdict[s]['vline-label'])
        plt.axhline(y=0, color='black')
        plt.legend(fontsize="8")

        plt.savefig(f'{dat.path_outdir}/figures_sens/{product}_{s}_{dat.time_str}.png')

        print(f'...{s} graphs saved to file')


    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')
