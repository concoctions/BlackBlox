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

from concrete_config import m3_concrete, concrete_life, k, A, DOC, EoL_calc, demo_CO2_LCI, r
from concrete_config import case_list, factory_list, f_suffix, factory_names, f_kwargs
from concrete_config import concrete_factory, concrete_CCS_factory




## RUN sensitivities
##---------------------------


def multi_sens(case_list=case_list, id='',reflines=None,  fast=True, ):
    print(f'\n#--START---################################################{datetime.now().strftime("%H%M")}\n')

    dat.default_scenario = "BASE"

    sdict = nested_dicts(2)

    sdict['electricity']['variable'] = 'fueltype'
    if fast is True:
        sdict['electricity']['options'] = ['grid electricity 0g/kWh','grid electricity 800g/kWh', ]
        sdict['electricity']['xticks'] = ['0', '800']
        sdict['electricity']['vline-loc'] = 0.4 
    else:
        sdict['electricity']['options'] = ['grid electricity 0g/kWh', 'grid electricity 200g/kWh', 'grid electricity 400g/kWh',  'grid electricity 600g/kWh', 'grid electricity 800g/kWh', 'grid electricity 1000g/kWh',] # ['electricity 360g/kWh', 'electricity 800g/kWh',] # 
        sdict['electricity']['xticks'] = ['0', '200', '400', '600', '800', '1000'] #  [360, 800]
        sdict['electricity']['vline-loc'] = 1.8 
    sdict['electricity']['chain'] = 'power'
    sdict['electricity']['unit'] = 'simple_power'
    sdict['electricity']['chain_CCS'] = ['power', 'CCS-power']
    sdict['electricity']['unit_CCS'] = ['simple_power', 'CCS_power']
    sdict['electricity']['fixed vars'] = [('combustion eff', 1.0)]
    sdict['electricity']['xlabel'] =  "g CO$_2$/kWh"
    sdict['electricity']['title'] = "net CO$_2$, by electricity CO$_2$ intensity"
    sdict['electricity']['vline-label'] = "natural gas"

    sdict['transport']['variable'] = 'transport km'
    if fast is True:
        sdict['transport']['options'] = [0, 400,]
        sdict['transport']['xticks'] = ['-100%', '+100%',]
        sdict['transport']['vline-loc'] = 0.5
    else:
        sdict['transport']['options'] = [0, 100, 200, 300, 400,]
        sdict['transport']['xticks'] = ['-100%', '-50%', '0%', '+50%', '+100%',]
        sdict['transport']['vline-loc'] = 2
    sdict['transport']['chain'] = ['concrete', 'concrete']
    sdict['transport']['unit'] = ['concrete-vol', 'cement_meal']
    sdict['transport']['chain_CCS'] = ['concrete', 'concrete']
    sdict['transport']['unit_CCS'] = ['concrete-vol', 'cement_meal']
    sdict['transport']['fixed vars'] = False
    sdict['transport']['xlabel'] =  "change from base case (road and rail tranpsort)"
    sdict['transport']['title'] = "net CO$_2$, by transport CO$_2$ intensity"
    sdict['transport']['vline-label'] = ""

    sdict['kiln-eff']['variable'] = 'fuel energy demand'
    if fast is True:
        sdict['kiln-eff']['options'] = [2.5, 4.0]
        sdict['kiln-eff']['xticks'] =  [2.5, 4.0]
        sdict['kiln-eff']['vline-loc'] = 0.5
    else:
        sdict['kiln-eff']['options'] = [2.5, 3.0, 3.5, 4.0]
        sdict['kiln-eff']['xticks'] =  [2.5, 3.0, 3.5, 4.0]
        sdict['kiln-eff']['vline-loc'] = 1.6
    sdict['kiln-eff']['chain'] = 'concrete'
    sdict['kiln-eff']['unit'] = 'cement_kiln-system'
    sdict['kiln-eff']['chain_CCS'] = 'concrete'
    sdict['kiln-eff']['unit_CCS'] = 'cement_kiln-system'
    sdict['kiln-eff']['fixed vars'] = False
    sdict['kiln-eff']['xlabel'] =  "GJ / t clinker"
    sdict['kiln-eff']['title'] = "net CO$_2$, by kiln fuel demand"
    sdict['kiln-eff']['vline-label'] = "base case (3.3)"

    sdict['co2-eff']['variable'] = 'Heat Demand'
    if fast is True:
        sdict['co2-eff']['options'] = [2.5, 4.0,]
        sdict['co2-eff']['xticks'] = [2.5, 4.0,]
        sdict['co2-eff']['vline-loc'] = 0.45
    else:
        sdict['co2-eff']['options'] = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
        sdict['co2-eff']['xticks'] = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
        sdict['co2-eff']['vline-loc'] = 2.4
    sdict['co2-eff']['chain'] = 'AC-CO2'
    sdict['co2-eff']['unit'] = 'duplicate_CO2capture'
    sdict['co2-eff']['chain_CCS'] = ['AC-CO2', 'CCS']
    sdict['co2-eff']['unit_CCS'] = ['duplicate_CO2capture', 'simple_CO2capture']
    sdict['co2-eff']['fixed vars'] = False
    sdict['co2-eff']['xticks'] = [2.0, 2.5, 3.0, 3.5, 4.0,]
    sdict['co2-eff']['xlabel'] =  "GJ / t CO$_2$ captured"
    sdict['co2-eff']['title'] = "net CO$_2$, by CO$_2$ Capture heat demand"
    sdict['co2-eff']['vline-label'] = ""

    sdict['co2-up']['variable'] = 'CO2 uptake eff'
    if fast is True:
            sdict['co2-up']['options'] = [0.2, 0.8]
            sdict['co2-up']['xticks'] = ['20%', '80%',]
            sdict['co2-up']['vline-loc'] = 0.67
    else:
        sdict['co2-up']['options'] = [0.2, 0.4, 0.6, 0.8]
        sdict['co2-up']['xticks'] = ['20%', '40%', '60%', '80%',]
        sdict['co2-up']['vline-loc'] = 3
    sdict['co2-up']['chain'] = 'concrete'
    sdict['co2-up']['unit'] = 'concrete-vol'
    sdict['co2-up']['chain_CCS'] = 'concrete'
    sdict['co2-up']['unit_CCS'] = 'concrete-vol'
    sdict['co2-up']['fixed vars'] = False
    sdict['co2-up']['xticks'] = ['20%', '40%', '60%', '80%',]
    sdict['co2-up']['xlabel'] =  "CO$_2$ uptake efficiency"
    sdict['co2-up']['title'] = "net CO$_2$, by CO$_2$ Injection Efficiency"
    sdict['co2-up']['vline-label'] = ""

    sdict['agg-recycle']['variable'] = 'recycled aggregate'
    if fast is True:
        sdict['agg-recycle']['options'] = [0.0, 1.0]
        sdict['agg-recycle']['xticks'] = ['0', '100%']
        sdict['agg-recycle']['vline-loc'] = 0
    else:
        sdict['agg-recycle']['options'] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        sdict['agg-recycle']['xticks'] = ['0', '20%', '40%', '60%', '80%', '100%']
        sdict['agg-recycle']['vline-loc'] = 0
    sdict['agg-recycle']['chain'] = 'concrete'
    sdict['agg-recycle']['unit'] = 'concrete-vol'
    sdict['agg-recycle']['chain_CCS'] = 'concrete'
    sdict['agg-recycle']['unit_CCS'] = 'concrete-vol'
    sdict['agg-recycle']['fixed vars'] = False
    sdict['agg-recycle']['xlabel'] =  "% recyclced aggregate use"
    sdict['agg-recycle']['title'] = "net CO$_2$, by recycled aggregate use"
    sdict['agg-recycle']['vline-label'] = ""


    Path(f'{dat.outdir}/figures_sens/').mkdir(parents=True, exist_ok=True)
    sens_net_dict = {}

    if id:
        id = id + '_'
        
    for s in sdict:

        print(f'...starting sensitivity analysis: {s} ({id})')        

        sens_dict = nested_dicts(2) # [case][df]

        for case in case_list:

            # without CCS - excel files output to factory folder
            in_df, out_df, agg_in_df, agg_out_df, net_df  = concrete_factory.run_sensitivity(product_qty=m3_concrete, 
                            scenario=case, 
                            chain_name=sdict[s]['chain'], 
                            unit_name=sdict[s]['unit'], 
                            variable=sdict[s]['variable'],
                            variable_options=sdict[s]['options'],
                            fixed_vars= sdict[s]['fixed vars'],
                            upstream_outflows=['CO2', 'CO2 infrastructure'],
                            upstream_inflows=['CO2 removed',],
                            aggregate_flows=['CO2', 'CO2__upstream', 'CO2 infrastructure'],
                            id=f'{id}_{case}'
                            )


            out_df = out_df.reset_index(level=0, drop=True)
            out_df.columns = sdict[s]['options']

            sens_dict[case]['out'] = out_df
            sens_dict[case]['agg_out'] = agg_out_df
            sens_dict[case]['agg_in'] = agg_in_df
                

            # with CCS - excel files output to factory folder
            in_df, out_df, agg_in_df, agg_out_df, net_df  = concrete_CCS_factory.run_sensitivity(product_qty=m3_concrete, 
                            scenario=case, 
                            chain_name=sdict[s]['chain_CCS'], 
                            unit_name=sdict[s]['unit_CCS'], 
                            variable=sdict[s]['variable'],
                            variable_options=sdict[s]['options'],
                            fixed_vars= sdict[s]['fixed vars'],
                            upstream_outflows=['CO2', 'CO2 infrastructure'],
                            upstream_inflows=['CO2 removed',],
                            aggregate_flows=['CO2', 'CO2__upstream', 'CO2 infrastructure'],
                            id=f'{id}_{case}'
                            )


            out_df = out_df.reset_index(level=0, drop=True)
            out_df.columns = sdict[s]['options']

            sens_dict[f'{case}-CCS']['out'] = out_df
            sens_dict[f'{case}-CCS']['agg_out'] = agg_out_df
            sens_dict[f'{case}-CCS']['agg_in'] = agg_in_df    


            if "BIO" in case:
                sens_dict[case]['color'] = '#006674'
                sens_dict[f'{case}-CCS']['color'] = '#d0d65a'
            else:
                sens_dict[case]['color'] = '#002942'
                sens_dict[f'{case}-CCS']['color'] = '#9f4a7f'

            if '03' in case:
                sens_dict[case]['linestyle'] = 'dotted'
                sens_dict[f'{case}-CCS']['linestyle'] = 'dotted'
            elif '10' in case or '15' in case:
                sens_dict[case]['linestyle'] = 'dashed'
                sens_dict[f'{case}-CCS']['linestyle'] = 'dashed'
            else:
                sens_dict[f'{case}-CCS']['linestyle'] = 'solid'
                sens_dict[case]['linestyle'] = 'solid'

        plt.figure()
        plt.style.context('seaborn')

        if id == '30mpa-ac':
            case_order = ['BASE', '03AC', '10AC',
                        'CCS - BASE', 'CCS - 03AC', 'CCS - 10AC', 
                        'BASE-BIO', '03AC-BIO', '10AC-BIO',
                        'CCS - BASE-BIO', 'CCS - 03AC-BIO', 'CCS - 10AC-BIO']

            case_names = ['Base', '0.3% AC', '10% AC',
                        'CCS', '0.3% AC, with CCS', '10% AC, with CCS', 
                        'Bioenergy',  '0.3% AC with Bioenergy', '10% AC with Bioenergy',
                        'BECCS', '0.3% AC with BECCS', '10% AC with BECCS']

        # elif id.startswith('cmu'):
        #     case_order = ['CMU', 'CMU15AC',
        #                     'CCS - CMU', 'CCS - CMU15AC', 
        #                     'CMU-BIO',  'CMU15AC-BIO', 
        #                     'CCS - CMU-BIO',  'CCS - CMU15AC-BIO']

        #     case_names = ['CMUs (8")', 'CMUs, 15% AC',
        #                   'CMUs with CCS', 'CMUs, 15% AC, with CCS',
        #                   'CMUs with Bioenergy',  'CMUS, 15% AC, with Bioenergy',
        #                   'CMUs with BECCS', 'CMUs, 15% AC, with Bioenergy']
        # else:
        case_order = [k for k in sens_dict]
        case_names = [k for k in sens_dict]

        for n, c in enumerate(case_order):
            CO2_out = list(sens_dict[c]['agg_out'].loc['CO2' , :])
            concrete_CO2 = list(sens_dict[c]['out'].loc['calcination CO2' , :])
            if '30mpa' in id:
                if '03' in c:
                        concrete_CO2 = [c * 0.597089056 for c in concrete_CO2]
                elif 'StrGain' in c:
                    concrete_CO2 = [c * 0.502968522 for c in concrete_CO2]
                elif '10' in c:
                        concrete_CO2 = [c * 0.502968522 for c in concrete_CO2]
                else:
                    concrete_CO2 = [c * 0.6 for c in concrete_CO2]
            elif 'cmu' in id:
                if '15' in c:
                    concrete_CO2 = [c * 0.454452783 for c in concrete_CO2]
                else:
                    concrete_CO2 = [c * 0.6 for c in concrete_CO2]
                    
            demo_CO2 = list(sens_dict[c]['out'].loc['concrete' , :])
            demo_CO2 = [d * demo_CO2_LCI for d in demo_CO2]

            if 'CO2__bio' in sens_dict[c]['out'].index:
                kiln_CO2 = list(sens_dict[c]['out'].loc['contrib kiln - CO2 bio', :])
                if 'contrib-charcoal - CO2 bio' in sens_dict[c]['out'].index:
                    charcoal_CO2 = list(sens_dict[c]['out'].loc['contrib-charcoal - CO2 bio' , :])
                else:
                    charcoal_CO2 = [0 for i in CO2_out]
                if 'contrib heat CCS - CO2 bio'  in sens_dict[c]['out'].index:
                    bioCCS_CO2 = list(sens_dict[c]['out'].loc['contrib heat CCS - CO2 bio' , :])
                else:
                    bioCCS_CO2 = [0 for i in CO2_out]
                
                bio_CO2 = [kiln_CO2[i]+charcoal_CO2[i]+bioCCS_CO2[i] for i in range(len(CO2_out))]
            else:
                bio_CO2 = [0 for i in CO2_out]

            net_CO2 = [(CO2_out[i] - bio_CO2[i] - concrete_CO2[i] + demo_CO2[i]) * 1000 for i in range(len(CO2_out))]

            for i, net in enumerate(net_CO2):
                sens_net_dict[f"{c} {s} {sdict[s]['options'][i]}"]  = net

            plt.plot(net_CO2, label=case_names[n], linestyle=sens_dict[c]['linestyle'], color=sens_dict[c]['color'])

        idx = np.asarray([i for i in range(len(sdict[s]['options']))])
        plt.xticks(ticks=idx, labels=sdict[s]['xticks'], rotation=65, fontsize="8")
        plt.ylabel("kg CO$_2$ per m$^3$ concrete")
        plt.xlabel(sdict[s]['xlabel'])
        plt.title(sdict[s]['title'])
        plt.yticks(np.arange(-50, 501, 100))
        plt.axvline(x=sdict[s]['vline-loc'], color='black', label=sdict[s]['vline-label'])
        plt.axhline(y=0, color='black')
        plt.legend(fontsize="8")

        plt.savefig(f'{dat.outdir}/figures_sens/{id}{s}.png')
        plt.close()

        print(f'...{s} graphs saved to file')

        sens_dict.clear()

    print(f'\n{datetime.now().strftime("%H%M")}##################################################--END---#\n')

    return sens_net_dict