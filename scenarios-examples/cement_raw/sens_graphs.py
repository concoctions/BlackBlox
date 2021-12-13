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
import pandas as pan
from pandas import ExcelWriter
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
sns.set_style("whitegrid")



def sens_graphs(net_CO2_dict, id, reflines=None):
    figdir = f'{dat.outdir}/figures_sens/main'
    Path(figdir).mkdir(parents=True, exist_ok=True) 

    # for k in net_CO2_dict:
    #     print(k, net_CO2_dict[k])

    p_dict = nested_dicts(2) #[plot][list]

    if id == '30mpa':
     # CO2 ORIGIN AND STRENGTH - absolute
        entry = p_dict['CO2 Origin']
        entry['net_CO2s'] = [
            # no strength gain
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC_bioAC'],
                net_CO2_dict['10AC-DAC'],
                net_CO2_dict['10AC-CCS-ownCO2'],
                net_CO2_dict['10AC-flue'],
                net_CO2_dict['10AC_bioAC-flue']],
            # strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain'] - 11.23,
                net_CO2_dict['10AC_StrGain-DAC'],
                net_CO2_dict['10AC_StrGain-CCS-ownCO2'],
                net_CO2_dict['10AC_StrGain-flue'],
                net_CO2_dict['10AC_StrGain-flue'] - 11.23]
            ]

        entry['net_CO2s_bottom'] = [
            # no strength gain, w avoided
            [net_CO2_dict['10AC'] - 16.856,
                net_CO2_dict['10AC_bioAC'] - 16.856,
                net_CO2_dict['10AC-DAC'],
                net_CO2_dict['10AC-CCS-ownCO2'],
                net_CO2_dict['10AC-flue'] - 16.856,
                net_CO2_dict['10AC_bioAC-flue'] - 16.856 ],
            # strength gain, w avoided 
            [net_CO2_dict['10AC_StrGain'] - 15.17,
                net_CO2_dict['10AC_StrGain'] - 11.23  - 15.17,
                net_CO2_dict['10AC_StrGain-DAC'],
                net_CO2_dict['10AC_StrGain-CCS-ownCO2'],
                net_CO2_dict['10AC_StrGain-flue']  - 15.17,
                net_CO2_dict['10AC_StrGain-flue'] - 11.23  - 15.17]
        ]

        entry['net_CO2_ref'] = [
            # no strength gain, w avoided
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE'],
                net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE'],
                net_CO2_dict['BASE']],
            # strength gain, w avoided 
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE'],
                net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE'],
                net_CO2_dict['BASE']]
        ]

        entry['labels'] = ['Pure CO$_2$,\nunaffiliated', 'Pure CO$_2$ unaff.,\n biogenic', 'Pure CO$_2$,\nfrom DAC', 'Pure CO$_2$,\nfrom own CCS', 'Flue gas', 'Flue gas,\nbiogenic']
        entry['line labels'] = ['no strength change', '+10% strength']
        entry['text'] = ''   
        entry['bottom'] = True
        entry['bottom text'] = ',\nwith avoided emissions'
        entry['line'] = ''
        entry['relative to'] = 'without AC'
        entry['title'] = 'Source of CO$_2$ for Accelerated Carbonation'

     # ELECTRICITY

        # 800g/kwh
        entry = p_dict['electricity']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['BASE electricity grid electricity 800g/kWh'],
                net_CO2_dict['BASE-CCS electricity grid electricity 800g/kWh'],
                net_CO2_dict['BASE-BIO electricity grid electricity 800g/kWh'],
                net_CO2_dict['BASE-BIO-CCS electricity grid electricity 800g/kWh']],
            # 0.3AC
            [net_CO2_dict['03AC electricity grid electricity 800g/kWh'],
                net_CO2_dict['03AC-CCS electricity grid electricity 800g/kWh'],
                net_CO2_dict['03AC-BIO electricity grid electricity 800g/kWh'],
                net_CO2_dict['03AC-BIO-CCS electricity grid electricity 800g/kWh']],
            # 10%AC
            [net_CO2_dict['10AC electricity grid electricity 800g/kWh'],
                net_CO2_dict['10AC-CCS electricity grid electricity 800g/kWh'],
                net_CO2_dict['10AC-BIO electricity grid electricity 800g/kWh'],
                net_CO2_dict['10AC-BIO-CCS electricity grid electricity 800g/kWh']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain electricity grid electricity 800g/kWh'],
                net_CO2_dict['10AC_StrGain-CCS electricity grid electricity 800g/kWh'],
                net_CO2_dict['10AC-BIO_StrGain electricity grid electricity 800g/kWh'],
                net_CO2_dict['10AC-BIO_StrGain-CCS electricity grid electricity 800g/kWh']],
            ]

        # 0g/kwh
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['BASE electricity grid electricity 0g/kWh'],
                net_CO2_dict['BASE-CCS electricity grid electricity 0g/kWh'],
                net_CO2_dict['BASE-BIO electricity grid electricity 0g/kWh'],
                net_CO2_dict['BASE-BIO-CCS electricity grid electricity 0g/kWh']],
            # 0.3AC
            [net_CO2_dict['03AC electricity grid electricity 0g/kWh'],
                net_CO2_dict['03AC-CCS electricity grid electricity 0g/kWh'],
                net_CO2_dict['03AC-BIO electricity grid electricity 0g/kWh'],
                net_CO2_dict['03AC-BIO-CCS electricity grid electricity 0g/kWh']],
            # 10%AC
            [net_CO2_dict['10AC electricity grid electricity 0g/kWh'],
                net_CO2_dict['10AC-CCS electricity grid electricity 0g/kWh'],
                net_CO2_dict['10AC-BIO electricity grid electricity 0g/kWh'],
                net_CO2_dict['10AC-BIO-CCS electricity grid electricity 0g/kWh']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain electricity grid electricity 0g/kWh'],
                net_CO2_dict['10AC_StrGain-CCS electricity grid electricity 0g/kWh'],
                net_CO2_dict['10AC-BIO_StrGain electricity grid electricity 0g/kWh'],
                net_CO2_dict['10AC-BIO_StrGain-CCS electricity grid electricity 0g/kWh']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  800g CO$_2$/kWh'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n   0g CO$_2$/kWh'
        entry['relative to'] = 'electricity from natural gas (370g CO$_2$/kWH)'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'CO$_2$ intensity of electricity'



     # TRANSPORT

        # twice as inefficient transport
        entry = p_dict['transport']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['BASE transport 400'],
                net_CO2_dict['BASE-CCS transport 400'],
                net_CO2_dict['BASE-BIO transport 400'],
                net_CO2_dict['BASE-BIO-CCS transport 400']],
            # 0.3AC
            [net_CO2_dict['03AC transport 400'],
                net_CO2_dict['03AC-CCS transport 400'],
                net_CO2_dict['03AC-BIO transport 400'],
                net_CO2_dict['03AC-BIO-CCS transport 400']],
            # 10%AC
            [net_CO2_dict['10AC transport 400'],
                net_CO2_dict['10AC-CCS transport 400'],
                net_CO2_dict['10AC-BIO transport 400'],
                net_CO2_dict['10AC-BIO-CCS transport 400']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain transport 400'],
                net_CO2_dict['10AC_StrGain-CCS transport 400'],
                net_CO2_dict['10AC-BIO_StrGain transport 400'],
                net_CO2_dict['10AC-BIO_StrGain-CCS transport 400']],
            ]

        # decarbonized transport
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['BASE transport 0'],
                net_CO2_dict['BASE-CCS transport 0'],
                net_CO2_dict['BASE-BIO transport 0'],
                net_CO2_dict['BASE-BIO-CCS transport 0']],
            # 0.3AC
            [net_CO2_dict['03AC transport 0'],
                net_CO2_dict['03AC-CCS transport 0'],
                net_CO2_dict['03AC-BIO transport 0'],
                net_CO2_dict['03AC-BIO-CCS transport 0']],
            # 10%AC
            [net_CO2_dict['10AC transport 0'],
                net_CO2_dict['10AC-CCS transport 0'],
                net_CO2_dict['10AC-BIO transport 0'],
                net_CO2_dict['10AC-BIO-CCS transport 0']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain transport 0'],
                net_CO2_dict['10AC_StrGain-CCS transport 0'],
                net_CO2_dict['10AC-BIO_StrGain transport 0'],
                net_CO2_dict['10AC-BIO_StrGain-CCS transport 0']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  +100%'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  -100%'
        entry['relative to'] = '200km, European average'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'CO$_2$ intensity of transpot'


     # KILN EFF

        # 4.0 GJ/t
        entry = p_dict['kiln eff']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['BASE kiln-eff 4.0'],
                net_CO2_dict['BASE-CCS kiln-eff 4.0'],
                net_CO2_dict['BASE-BIO kiln-eff 4.0'],
                net_CO2_dict['BASE-BIO-CCS kiln-eff 4.0']],
            # 0.3AC
            [net_CO2_dict['03AC kiln-eff 4.0'],
                net_CO2_dict['03AC-CCS kiln-eff 4.0'],
                net_CO2_dict['03AC-BIO kiln-eff 4.0'],
                net_CO2_dict['03AC-BIO-CCS kiln-eff 4.0']],
            # 10%AC
            [net_CO2_dict['10AC kiln-eff 4.0'],
                net_CO2_dict['10AC-CCS kiln-eff 4.0'],
                net_CO2_dict['10AC-BIO kiln-eff 4.0'],
                net_CO2_dict['10AC-BIO-CCS kiln-eff 4.0']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain kiln-eff 4.0'],
                net_CO2_dict['10AC_StrGain-CCS kiln-eff 4.0'],
                net_CO2_dict['10AC-BIO_StrGain kiln-eff 4.0'],
                net_CO2_dict['10AC-BIO_StrGain-CCS kiln-eff 4.0']],
            ]

        # 2.5 GJ/t concrete
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['BASE kiln-eff 2.5'],
                net_CO2_dict['BASE-CCS kiln-eff 2.5'],
                net_CO2_dict['BASE-BIO kiln-eff 2.5'],
                net_CO2_dict['BASE-BIO-CCS kiln-eff 2.5']],
            # 0.3AC
            [net_CO2_dict['03AC kiln-eff 2.5'],
                net_CO2_dict['03AC-CCS kiln-eff 2.5'],
                net_CO2_dict['03AC-BIO kiln-eff 2.5'],
                net_CO2_dict['03AC-BIO-CCS kiln-eff 2.5']],
            # 10%AC
            [net_CO2_dict['10AC kiln-eff 2.5'],
                net_CO2_dict['10AC-CCS kiln-eff 2.5'],
                net_CO2_dict['10AC-BIO kiln-eff 2.5'],
                net_CO2_dict['10AC-BIO-CCS kiln-eff 2.5']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain kiln-eff 2.5'],
                net_CO2_dict['10AC_StrGain-CCS kiln-eff 2.5'],
                net_CO2_dict['10AC-BIO_StrGain kiln-eff 2.5'],
                net_CO2_dict['10AC-BIO_StrGain-CCS kiln-eff 2.5']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  4 GJ/t clinker'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  2.5 GJ/t clinker'
        entry['relative to'] = '3.3 GJ/t clinker'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Clinker Kiln Thermal Efficiency'


     # CO2 EFF

        # 4.0 GJ/t
        entry = p_dict['CO2 eff']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['BASE co2-eff 4.0'],
                net_CO2_dict['BASE-CCS co2-eff 4.0'],
                net_CO2_dict['BASE-BIO co2-eff 4.0'],
                net_CO2_dict['BASE-BIO-CCS co2-eff 4.0']],
            # 0.3AC
            [net_CO2_dict['03AC co2-eff 4.0'],
                net_CO2_dict['03AC-CCS co2-eff 4.0'],
                net_CO2_dict['03AC-BIO co2-eff 4.0'],
                net_CO2_dict['03AC-BIO-CCS co2-eff 4.0']],
            # 10%AC
            [net_CO2_dict['10AC co2-eff 4.0'],
                net_CO2_dict['10AC-CCS co2-eff 4.0'],
                net_CO2_dict['10AC-BIO co2-eff 4.0'],
                net_CO2_dict['10AC-BIO-CCS co2-eff 4.0']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain co2-eff 4.0'],
                net_CO2_dict['10AC_StrGain-CCS co2-eff 4.0'],
                net_CO2_dict['10AC-BIO_StrGain co2-eff 4.0'],
                net_CO2_dict['10AC-BIO_StrGain-CCS co2-eff 4.0']],
            ]

        # 2.5 GJ/t concrete
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['BASE co2-eff 2.5'],
                net_CO2_dict['BASE-CCS co2-eff 2.5'],
                net_CO2_dict['BASE-BIO co2-eff 2.5'],
                net_CO2_dict['BASE-BIO-CCS co2-eff 2.5']],
            # 0.3AC
            [net_CO2_dict['03AC co2-eff 2.5'],
                net_CO2_dict['03AC-CCS co2-eff 2.5'],
                net_CO2_dict['03AC-BIO co2-eff 2.5'],
                net_CO2_dict['03AC-BIO-CCS co2-eff 2.5']],
            # 10%AC
            [net_CO2_dict['10AC co2-eff 2.5'],
                net_CO2_dict['10AC-CCS co2-eff 2.5'],
                net_CO2_dict['10AC-BIO co2-eff 2.5'],
                net_CO2_dict['10AC-BIO-CCS co2-eff 2.5']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain co2-eff 2.5'],
                net_CO2_dict['10AC_StrGain-CCS co2-eff 2.5'],
                net_CO2_dict['10AC-BIO_StrGain co2-eff 2.5'],
                net_CO2_dict['10AC-BIO_StrGain-CCS co2-eff 2.5']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  4 GJ/t CO$_2$'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  2.5 GJ/t CO$_2$'
        entry['relative to'] = '3.2 GJ/t CO$_2$'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'CO$_2$ Capture Reboiler Thermal Efficiency'

     # CO2 INJECTION

        # 20% efficient
        entry = p_dict['CO2 injection']

        entry['net_CO2s_bottom'] = [
            # no AC 
            [net_CO2_dict['BASE co2-up 0.2'],
                net_CO2_dict['BASE-CCS co2-up 0.2'],
                net_CO2_dict['BASE-BIO co2-up 0.2'],
                net_CO2_dict['BASE-BIO-CCS co2-up 0.2']],
            # 0.3AC
            [net_CO2_dict['03AC co2-up 0.2'],
                net_CO2_dict['03AC-CCS co2-up 0.2'],
                net_CO2_dict['03AC-BIO co2-up 0.2'],
                net_CO2_dict['03AC-BIO-CCS co2-up 0.2']],
            # 10%AC
            [net_CO2_dict['10AC co2-up 0.2'],
                net_CO2_dict['10AC-CCS co2-up 0.2'],
                net_CO2_dict['10AC-BIO co2-up 0.2'],
                net_CO2_dict['10AC-BIO-CCS co2-up 0.2']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain co2-up 0.2'],
                net_CO2_dict['10AC_StrGain-CCS co2-up 0.2'],
                net_CO2_dict['10AC-BIO_StrGain co2-up 0.2'],
                net_CO2_dict['10AC-BIO_StrGain-CCS co2-up 0.2']],
            ]

        # 80% efficient
        entry['net_CO2s'] =[
            # no AC 
            [net_CO2_dict['BASE co2-up 0.8'],
                net_CO2_dict['BASE-CCS co2-up 0.8'],
                net_CO2_dict['BASE-BIO co2-up 0.8'],
                net_CO2_dict['BASE-BIO-CCS co2-up 0.8']],
            # 0.3AC
            [net_CO2_dict['03AC co2-up 0.8'],
                net_CO2_dict['03AC-CCS co2-up 0.8'],
                net_CO2_dict['03AC-BIO co2-up 0.8'],
                net_CO2_dict['03AC-BIO-CCS co2-up 0.8']],
            # 10%AC
            [net_CO2_dict['10AC co2-up 0.8'],
                net_CO2_dict['10AC-CCS co2-up 0.8'],
                net_CO2_dict['10AC-BIO co2-up 0.8'],
                net_CO2_dict['10AC-BIO-CCS co2-up 0.8']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain co2-up 0.8'],
                net_CO2_dict['10AC_StrGain-CCS co2-up 0.8'],
                net_CO2_dict['10AC-BIO_StrGain co2-up 0.8'],
                net_CO2_dict['10AC-BIO_StrGain-CCS co2-up 0.8']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  80% CO$_2$ uptake'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  20% CO$_2$ uptake'
        entry['relative to'] = '40% CO$_2$ uptake'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Accelerated Carbonation CO$_2$ Injection Efficiency'


     # AGGREGATE

        # 100% recycled
        entry = p_dict['aggregate']

        entry['net_CO2s_bottom'] = [
            # no AC 
            [net_CO2_dict['BASE agg-recycle 1.0'],
                net_CO2_dict['BASE-CCS agg-recycle 1.0'],
                net_CO2_dict['BASE-BIO agg-recycle 1.0'],
                net_CO2_dict['BASE-BIO-CCS agg-recycle 1.0']],
            # 0.3AC
            [net_CO2_dict['03AC agg-recycle 1.0'],
                net_CO2_dict['03AC-CCS agg-recycle 1.0'],
                net_CO2_dict['03AC-BIO agg-recycle 1.0'],
                net_CO2_dict['03AC-BIO-CCS agg-recycle 1.0']],
            # 10%AC
            [net_CO2_dict['10AC agg-recycle 1.0'],
                net_CO2_dict['10AC-CCS agg-recycle 1.0'],
                net_CO2_dict['10AC-BIO agg-recycle 1.0'],
                net_CO2_dict['10AC-BIO-CCS agg-recycle 1.0']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain agg-recycle 1.0'],
                net_CO2_dict['10AC_StrGain-CCS agg-recycle 1.0'],
                net_CO2_dict['10AC-BIO_StrGain agg-recycle 1.0'],
                net_CO2_dict['10AC-BIO_StrGain-CCS agg-recycle 1.0']],
            ]

        # 0% recycled
        entry['net_CO2s'] =[
            # no AC 
            [net_CO2_dict['BASE agg-recycle 0.0'],
                net_CO2_dict['BASE-CCS agg-recycle 0.0'],
                net_CO2_dict['BASE-BIO agg-recycle 0.0'],
                net_CO2_dict['BASE-BIO-CCS agg-recycle 0.0']],
            # 0.3AC
            [net_CO2_dict['03AC agg-recycle 0.0'],
                net_CO2_dict['03AC-CCS agg-recycle 0.0'],
                net_CO2_dict['03AC-BIO agg-recycle 0.0'],
                net_CO2_dict['03AC-BIO-CCS agg-recycle 0.0']],
            # 10%AC
            [net_CO2_dict['10AC agg-recycle 0.0'],
                net_CO2_dict['10AC-CCS agg-recycle 0.0'],
                net_CO2_dict['10AC-BIO agg-recycle 0.0'],
                net_CO2_dict['10AC-BIO-CCS agg-recycle 0.0']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain agg-recycle 0.0'],
                net_CO2_dict['10AC_StrGain-CCS agg-recycle 0.0'],
                net_CO2_dict['10AC-BIO_StrGain agg-recycle 0.0'],
                net_CO2_dict['10AC-BIO_StrGain-CCS agg-recycle 0.0']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  no recycled aggreate'        
        entry['bottom'] = True
        entry['bottom text'] = ',\n  100% recycled aggreate'
        entry['relative to'] = 'no recycled aggregate'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Recycled Aggregate Use'


     # DEMOLITION

        # 0% carbonated
        entry = p_dict['demolition']

        entry['net_CO2s_bottom'] = [
            # no AC 
            [net_CO2_dict['BASE demolition none'],
                net_CO2_dict['BASE-CCS demolition none'],
                net_CO2_dict['BASE-BIO demolition none'],
                net_CO2_dict['BASE-BIO-CCS demolition none']],
            # 0.3AC
            [net_CO2_dict['03AC demolition none'],
                net_CO2_dict['03AC-CCS demolition none'],
                net_CO2_dict['03AC-BIO demolition none'],
                net_CO2_dict['03AC-BIO-CCS demolition none']],
            # 10%AC
            [net_CO2_dict['10AC demolition none'],
                net_CO2_dict['10AC-CCS demolition none'],
                net_CO2_dict['10AC-BIO demolition none'],
                net_CO2_dict['10AC-BIO-CCS demolition none']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain demolition none'],
                net_CO2_dict['10AC_StrGain-CCS demolition none'],
                net_CO2_dict['10AC-BIO_StrGain demolition none'],
                net_CO2_dict['10AC-BIO_StrGain-CCS demolition none']],
            ]

        # 80% carbonated
        entry['net_CO2s'] =[
            # no AC 
            [net_CO2_dict['BASE demolition to 80%'],
                net_CO2_dict['BASE-CCS demolition to 80%'],
                net_CO2_dict['BASE-BIO demolition to 80%'],
                net_CO2_dict['BASE-BIO-CCS demolition to 80%']],
            # 0.3AC
            [net_CO2_dict['03AC demolition to 80%'],
                net_CO2_dict['03AC-CCS demolition to 80%'],
                net_CO2_dict['03AC-BIO demolition to 80%'],
                net_CO2_dict['03AC-BIO-CCS demolition to 80%']],
            # 10%AC
            [net_CO2_dict['10AC demolition to 80%'],
                net_CO2_dict['10AC-CCS demolition to 80%'],
                net_CO2_dict['10AC-BIO demolition to 80%'],
                net_CO2_dict['10AC-BIO-CCS demolition to 80%']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain demolition to 80%'],
                net_CO2_dict['10AC_StrGain-CCS demolition to 80%'],
                net_CO2_dict['10AC-BIO_StrGain demolition to 80%'],
                net_CO2_dict['10AC-BIO_StrGain-CCS demolition to 80%']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  carbonation to 80% of calcination CO$_2$'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  no further carbonation'
        entry['relative to'] = 'no further carbonation'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Additional carbonation during demolition and recovery'

     # SERVICE LIFE

        # 25 years
        entry = p_dict['servicelife']

        entry['net_CO2s'] = [
            # no AC
            [net_CO2_dict['BASE servicelife 25 years'],
                net_CO2_dict['BASE-CCS servicelife 25 years'],
                net_CO2_dict['BASE-BIO servicelife 25 years'],
                net_CO2_dict['BASE-BIO-CCS servicelife 25 years']],
            # 0.3AC
            [net_CO2_dict['03AC servicelife 25 years'],
                net_CO2_dict['03AC-CCS servicelife 25 years'],
                net_CO2_dict['03AC-BIO servicelife 25 years'],
                net_CO2_dict['03AC-BIO-CCS servicelife 25 years']],
            # 10%AC
            [net_CO2_dict['10AC servicelife 25 years'],
                net_CO2_dict['10AC-CCS servicelife 25 years'],
                net_CO2_dict['10AC-BIO servicelife 25 years'],
                net_CO2_dict['10AC-BIO-CCS servicelife 25 years']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain servicelife 25 years'],
                net_CO2_dict['10AC_StrGain-CCS servicelife 25 years'],
                net_CO2_dict['10AC-BIO_StrGain servicelife 25 years'],
                net_CO2_dict['10AC-BIO_StrGain-CCS servicelife 25 years']],
            ]

        # 200 years
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['BASE servicelife 200 years'],
                net_CO2_dict['BASE-CCS servicelife 200 years'],
                net_CO2_dict['BASE-BIO servicelife 200 years'],
                net_CO2_dict['BASE-BIO-CCS servicelife 200 years']],
            # 0.3AC
            [net_CO2_dict['03AC servicelife 200 years'],
                net_CO2_dict['03AC-CCS servicelife 200 years'],
                net_CO2_dict['03AC-BIO servicelife 200 years'],
                net_CO2_dict['03AC-BIO-CCS servicelife 200 years']],
            # 10%AC
            [net_CO2_dict['10AC servicelife 200 years'],
                net_CO2_dict['10AC-CCS servicelife 200 years'],
                net_CO2_dict['10AC-BIO servicelife 200 years'],
                net_CO2_dict['10AC-BIO-CCS servicelife 200 years']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain servicelife 200 years'],
                net_CO2_dict['10AC_StrGain-CCS servicelife 200 years'],
                net_CO2_dict['10AC-BIO_StrGain servicelife 200 years'],
                net_CO2_dict['10AC-BIO_StrGain-CCS servicelife 200 years']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  25 years'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  200 years'
        entry['relative to'] = '50 years'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Concrete First Use Life'

     # EXPOSURE

        # 25 years
        entry = p_dict['exposure']

        entry['net_CO2s_bottom'] = [
            # no AC
            [net_CO2_dict['BASE exposure outdoor, sheltered'],
                net_CO2_dict['BASE-CCS exposure outdoor, sheltered'],
                net_CO2_dict['BASE-BIO exposure outdoor, sheltered'],
                net_CO2_dict['BASE-BIO-CCS exposure outdoor, sheltered']],
            # 0.3AC
            [net_CO2_dict['03AC exposure outdoor, sheltered'],
                net_CO2_dict['03AC-CCS exposure outdoor, sheltered'],
                net_CO2_dict['03AC-BIO exposure outdoor, sheltered'],
                net_CO2_dict['03AC-BIO-CCS exposure outdoor, sheltered']],
            # 10%AC
            [net_CO2_dict['10AC exposure outdoor, sheltered'],
                net_CO2_dict['10AC-CCS exposure outdoor, sheltered'],
                net_CO2_dict['10AC-BIO exposure outdoor, sheltered'],
                net_CO2_dict['10AC-BIO-CCS exposure outdoor, sheltered']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain exposure outdoor, sheltered'],
                net_CO2_dict['10AC_StrGain-CCS exposure outdoor, sheltered'],
                net_CO2_dict['10AC-BIO_StrGain exposure outdoor, sheltered'],
                net_CO2_dict['10AC-BIO_StrGain-CCS exposure outdoor, sheltered']],
            ]

        entry['net_CO2s'] =[
            # no AC 
            [net_CO2_dict['BASE exposure in ground'],
                net_CO2_dict['BASE-CCS exposure in ground'],
                net_CO2_dict['BASE-BIO exposure in ground'],
                net_CO2_dict['BASE-BIO-CCS exposure in ground']],
            # 0.3AC
            [net_CO2_dict['03AC exposure in ground'],
                net_CO2_dict['03AC-CCS exposure in ground'],
                net_CO2_dict['03AC-BIO exposure in ground'],
                net_CO2_dict['03AC-BIO-CCS exposure in ground']],
            # 10%AC
            [net_CO2_dict['10AC exposure in ground'],
                net_CO2_dict['10AC-CCS exposure in ground'],
                net_CO2_dict['10AC-BIO exposure in ground'],
                net_CO2_dict['10AC-BIO-CCS exposure in ground']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain exposure in ground'],
                net_CO2_dict['10AC_StrGain-CCS exposure in ground'],
                net_CO2_dict['10AC-BIO_StrGain exposure in ground'],
                net_CO2_dict['10AC-BIO_StrGain-CCS exposure in ground']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['BASE'],
                net_CO2_dict['BASE-CCS'],
                net_CO2_dict['BASE-BIO'],
                net_CO2_dict['BASE-BIO-CCS']],
            # 0.3AC
            [net_CO2_dict['03AC'],
                net_CO2_dict['03AC-CCS'],
                net_CO2_dict['03AC-BIO'],
                net_CO2_dict['03AC-BIO-CCS']],
            # 10%AC
            [net_CO2_dict['10AC'],
                net_CO2_dict['10AC-CCS'],
                net_CO2_dict['10AC-BIO'],
                net_CO2_dict['10AC-BIO-CCS']],
            # 10%AC - strength gain
            [net_CO2_dict['10AC_StrGain'],
                net_CO2_dict['10AC_StrGain-CCS'],
                net_CO2_dict['10AC-BIO_StrGain'],
                net_CO2_dict['10AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '0.3% injection', '10% Cure', '10% Cure, +10% strength']
        entry['text'] = ',\n  in ground'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  outdoor sheltered'
        entry['relative to'] = '50% outdoor exposed, 50% indoor, covered'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Concrete Exposure'


    if id == 'cmu':
     # CO2 ORIGIN AND STRENGTH - absolute
        entry = p_dict['CO2 Origin']
        entry['net_CO2s'] = [
            # no strength gain
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC_bioAC'],
                net_CO2_dict['CMU15AC-DAC'],
                net_CO2_dict['CMU15AC-CCS-ownCO2'],
                net_CO2_dict['CMU15AC-flue'],
                net_CO2_dict['CMU15AC_bioAC-flue']],
            # strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain'] - 8.95,
                net_CO2_dict['CMU15AC_StrGain-DAC'],
                net_CO2_dict['CMU15AC_StrGain-CCS-ownCO2'],
                net_CO2_dict['CMU15AC_StrGain-flue'],
                net_CO2_dict['CMU15AC_StrGain-flue'] - 8.95]
            ]

        entry['net_CO2s_bottom'] = [
            # no strength gain, w avoided
            [net_CO2_dict['CMU15AC'] - 14.924,
                net_CO2_dict['CMU15AC_bioAC'] - 14.924,
                net_CO2_dict['CMU15AC-DAC'],
                net_CO2_dict['CMU15AC-CCS-ownCO2'],
                net_CO2_dict['CMU15AC-flue'] - 14.924,
                net_CO2_dict['CMU15AC_bioAC-flue'] - 14.924 ],
            # strength gain, w avoided 
            [net_CO2_dict['CMU15AC_StrGain'] - 13.428,
                net_CO2_dict['CMU15AC_StrGain'] - 8.95  - 13.428,
                net_CO2_dict['CMU15AC_StrGain-DAC'],
                net_CO2_dict['CMU15AC_StrGain-CCS-ownCO2'],
                net_CO2_dict['CMU15AC_StrGain-flue']  - 13.428,
                net_CO2_dict['CMU15AC_StrGain-flue'] - 8.95  - 13.428]
        ]

        entry['net_CO2_ref'] = [
            # no strength gain, w avoided
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU'],
                net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU'],
                net_CO2_dict['CMU']],
            # strength gain, w avoided 
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU'],
                net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU'],
                net_CO2_dict['CMU']]
        ]

        entry['labels'] = ['Pure CO$_2$,\nunaffiliated', 'Pure CO$_2$ unaff.,\n biogenic', 'Pure CO$_2$,\nfrom DAC', 'Pure CO$_2$,\nfrom own CCS', 'Flue gas', 'Flue gas,\nbiogenic']
        entry['line labels'] = ['no strength change', '+10% strength']
        entry['text'] = ''   
        entry['bottom'] = True
        entry['bottom text'] = ',\nwith avoided emissions'
        entry['line'] = ''
        entry['relative to'] = 'without AC'
        entry['title'] = 'Source of CO$_2$ for Accelerated Carbonation'

     # ELECTRICITY

        # 800g/kwh
        entry = p_dict['electricity']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['CMU electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU-CCS electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU-BIO electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU-BIO-CCS electricity grid electricity 800g/kWh']],
            # 15%AC
            [net_CO2_dict['CMU15AC electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU15AC-CCS electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU15AC-BIO electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU15AC-BIO-CCS electricity grid electricity 800g/kWh']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU15AC_StrGain-CCS electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU15AC-BIO_StrGain electricity grid electricity 800g/kWh'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS electricity grid electricity 800g/kWh']],
            ]

        # 0g/kwh
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['CMU electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU-CCS electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU-BIO electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU-BIO-CCS electricity grid electricity 0g/kWh']],
            # 15%AC
            [net_CO2_dict['CMU15AC electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU15AC-CCS electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU15AC-BIO electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU15AC-BIO-CCS electricity grid electricity 0g/kWh']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU15AC_StrGain-CCS electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU15AC-BIO_StrGain electricity grid electricity 0g/kWh'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS electricity grid electricity 0g/kWh']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['CMU', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC',  '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  800g CO2/kWh'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n   0g CO2/kWh'
        entry['relative to'] = 'electricity from natural gas (370g CO2/kWH)'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'CO$_2$ intensity of electricity'


     # TRANSPORT

        # twice as inefficient transport
        entry = p_dict['transport']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['CMU transport 400'],
                net_CO2_dict['CMU-CCS transport 400'],
                net_CO2_dict['CMU-BIO transport 400'],
                net_CO2_dict['CMU-BIO-CCS transport 400']],
            # 15%AC
            [net_CO2_dict['CMU15AC transport 400'],
                net_CO2_dict['CMU15AC-CCS transport 400'],
                net_CO2_dict['CMU15AC-BIO transport 400'],
                net_CO2_dict['CMU15AC-BIO-CCS transport 400']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain transport 400'],
                net_CO2_dict['CMU15AC_StrGain-CCS transport 400'],
                net_CO2_dict['CMU15AC-BIO_StrGain transport 400'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS transport 400']],
            ]

        # decarbonized transport
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['CMU transport 0'],
                net_CO2_dict['CMU-CCS transport 0'],
                net_CO2_dict['CMU-BIO transport 0'],
                net_CO2_dict['CMU-BIO-CCS transport 0']],
            # 15%AC
            [net_CO2_dict['CMU15AC transport 0'],
                net_CO2_dict['CMU15AC-CCS transport 0'],
                net_CO2_dict['CMU15AC-BIO transport 0'],
                net_CO2_dict['CMU15AC-BIO-CCS transport 0']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain transport 0'],
                net_CO2_dict['CMU15AC_StrGain-CCS transport 0'],
                net_CO2_dict['CMU15AC-BIO_StrGain transport 0'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS transport 0']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['CMU', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC',  '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  +100%'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  -100%'
        entry['relative to'] = '200km, European average'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'CO$_2$ intensity of transpot'

     # KILN EFF

        # 4.0 GJ/t
        entry = p_dict['kiln eff']

        entry['net_CO2s']= [
            # no AC 
            [net_CO2_dict['CMU kiln-eff 4.0'],
                net_CO2_dict['CMU-CCS kiln-eff 4.0'],
                net_CO2_dict['CMU-BIO kiln-eff 4.0'],
                net_CO2_dict['CMU-BIO-CCS kiln-eff 4.0']],
            # 15%AC
            [net_CO2_dict['CMU15AC kiln-eff 4.0'],
                net_CO2_dict['CMU15AC-CCS kiln-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO kiln-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO-CCS kiln-eff 4.0']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain kiln-eff 4.0'],
                net_CO2_dict['CMU15AC_StrGain-CCS kiln-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain kiln-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS kiln-eff 4.0']],
            ]

        # 2.5 GJ/t concrete
        entry['net_CO2s_bottom'] = [
            # no AC 
            [net_CO2_dict['CMU kiln-eff 2.5'],
                net_CO2_dict['CMU-CCS kiln-eff 2.5'],
                net_CO2_dict['CMU-BIO kiln-eff 2.5'],
                net_CO2_dict['CMU-BIO-CCS kiln-eff 2.5']],
            # 15%AC
            [net_CO2_dict['CMU15AC kiln-eff 2.5'],
                net_CO2_dict['CMU15AC-CCS kiln-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO kiln-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO-CCS kiln-eff 2.5']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain kiln-eff 2.5'],
                net_CO2_dict['CMU15AC_StrGain-CCS kiln-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO_StrGain kiln-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS kiln-eff 2.5']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['CMU', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC',  '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  4 GJ/t clinker'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  2.5 GJ/t clinker'
        entry['relative to'] = '3.3 GJ/t clinker'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Clinker Kiln Thermal Efficiency'


     # CO2 EFF

        # 4.0 GJ/t
        entry = p_dict['CO2 eff']

        entry['net_CO2s']  = [
            # no AC 
            [net_CO2_dict['CMU co2-eff 4.0'],
                net_CO2_dict['CMU-CCS co2-eff 4.0'],
                net_CO2_dict['CMU-BIO co2-eff 4.0'],
                net_CO2_dict['CMU-BIO-CCS co2-eff 4.0']],
            # 15%AC
            [net_CO2_dict['CMU15AC co2-eff 4.0'],
                net_CO2_dict['CMU15AC-CCS co2-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO co2-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO-CCS co2-eff 4.0']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain co2-eff 4.0'],
                net_CO2_dict['CMU15AC_StrGain-CCS co2-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain co2-eff 4.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS co2-eff 4.0']],
            ]

        # 2.5 GJ/t concrete
        entry['net_CO2s_bottom']  =[
            # no AC 
            [net_CO2_dict['CMU co2-eff 2.5'],
                net_CO2_dict['CMU-CCS co2-eff 2.5'],
                net_CO2_dict['CMU-BIO co2-eff 2.5'],
                net_CO2_dict['CMU-BIO-CCS co2-eff 2.5']],
            # 15%AC
            [net_CO2_dict['CMU15AC co2-eff 2.5'],
                net_CO2_dict['CMU15AC-CCS co2-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO co2-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO-CCS co2-eff 2.5']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain co2-eff 2.5'],
                net_CO2_dict['CMU15AC_StrGain-CCS co2-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO_StrGain co2-eff 2.5'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS co2-eff 2.5']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['CMU', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC',  '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  4 GJ/t CO$_2$'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  2.5 GJ/t CO$_2$'
        entry['relative to'] = '3.2 GJ/t CO$_2$'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'CO$_2$ Capture Reboiler Thermal Efficiency'

     # CO2 INJECTION

        # 80% efficient
        entry = p_dict['CO2 injection']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['CMU co2-up 0.2'],
                net_CO2_dict['CMU-CCS co2-up 0.2'],
                net_CO2_dict['CMU-BIO co2-up 0.2'],
                net_CO2_dict['CMU-BIO-CCS co2-up 0.2']],
            # 15%AC
            [net_CO2_dict['CMU15AC co2-up 0.2'],
                net_CO2_dict['CMU15AC-CCS co2-up 0.2'],
                net_CO2_dict['CMU15AC-BIO co2-up 0.2'],
                net_CO2_dict['CMU15AC-BIO-CCS co2-up 0.2']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain co2-up 0.2'],
                net_CO2_dict['CMU15AC_StrGain-CCS co2-up 0.2'],
                net_CO2_dict['CMU15AC-BIO_StrGain co2-up 0.2'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS co2-up 0.2']],
            ]

        # 20% efficient
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['CMU co2-up 0.8'],
                net_CO2_dict['CMU-CCS co2-up 0.8'],
                net_CO2_dict['CMU-BIO co2-up 0.8'],
                net_CO2_dict['CMU-BIO-CCS co2-up 0.8']],
            # 15%AC
            [net_CO2_dict['CMU15AC co2-up 0.8'],
                net_CO2_dict['CMU15AC-CCS co2-up 0.8'],
                net_CO2_dict['CMU15AC-BIO co2-up 0.8'],
                net_CO2_dict['CMU15AC-BIO-CCS co2-up 0.8']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain co2-up 0.8'],
                net_CO2_dict['CMU15AC_StrGain-CCS co2-up 0.8'],
                net_CO2_dict['CMU15AC-BIO_StrGain co2-up 0.8'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS co2-up 0.8']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['CMU', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC',  '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  80% CO$_2$ uptake'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  20% CO$_2$ uptake'
        entry['relative to'] = '40% CO$_2$ uptake'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Accelerated Carbonation CO$_2$ Injection Efficiency'


     # AGGREGATE

        # 100% recycled
        entry = p_dict['aggregate']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['CMU agg-recycle 1.0'],
                net_CO2_dict['CMU-CCS agg-recycle 1.0'],
                net_CO2_dict['CMU-BIO agg-recycle 1.0'],
                net_CO2_dict['CMU-BIO-CCS agg-recycle 1.0']],
            # 15%AC
            [net_CO2_dict['CMU15AC agg-recycle 1.0'],
                net_CO2_dict['CMU15AC-CCS agg-recycle 1.0'],
                net_CO2_dict['CMU15AC-BIO agg-recycle 1.0'],
                net_CO2_dict['CMU15AC-BIO-CCS agg-recycle 1.0']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain agg-recycle 1.0'],
                net_CO2_dict['CMU15AC_StrGain-CCS agg-recycle 1.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain agg-recycle 1.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS agg-recycle 1.0']],
            ]

        # 0% recycled
        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['CMU agg-recycle 0.0'],
                net_CO2_dict['CMU-CCS agg-recycle 0.0'],
                net_CO2_dict['CMU-BIO agg-recycle 0.0'],
                net_CO2_dict['CMU-BIO-CCS agg-recycle 0.0']],
            # 15%AC
            [net_CO2_dict['CMU15AC agg-recycle 0.0'],
                net_CO2_dict['CMU15AC-CCS agg-recycle 0.0'],
                net_CO2_dict['CMU15AC-BIO agg-recycle 0.0'],
                net_CO2_dict['CMU15AC-BIO-CCS agg-recycle 0.0']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain agg-recycle 0.0'],
                net_CO2_dict['CMU15AC_StrGain-CCS agg-recycle 0.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain agg-recycle 0.0'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS agg-recycle 0.0']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['CMU', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC',  '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  100% recycled aggreate'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  no recycled aggreate'
        entry['relative to'] = 'no recycled aggregate'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Recycled Aggregate Use'


     # DEMOLITION

        # 0% carbonated
        entry = p_dict['demolition']

        entry['net_CO2s_bottom'] = [
            # no AC 
            [net_CO2_dict['CMU demolition none'],
                net_CO2_dict['CMU-CCS demolition none'],
                net_CO2_dict['CMU-BIO demolition none'],
                net_CO2_dict['CMU-BIO-CCS demolition none']],
            # 15%AC
            [net_CO2_dict['CMU15AC demolition none'],
                net_CO2_dict['CMU15AC-CCS demolition none'],
                net_CO2_dict['CMU15AC-BIO demolition none'],
                net_CO2_dict['CMU15AC-BIO-CCS demolition none']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain demolition none'],
                net_CO2_dict['CMU15AC_StrGain-CCS demolition none'],
                net_CO2_dict['CMU15AC-BIO_StrGain demolition none'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS demolition none']],
            ]

        # 80% carbonated
        entry['net_CO2s'] =[
            # no AC 
            [net_CO2_dict['CMU demolition to 80%'],
                net_CO2_dict['CMU-CCS demolition to 80%'],
                net_CO2_dict['CMU-BIO demolition to 80%'],
                net_CO2_dict['CMU-BIO-CCS demolition to 80%']],
            # 15%AC
            [net_CO2_dict['CMU15AC demolition to 80%'],
                net_CO2_dict['CMU15AC-CCS demolition to 80%'],
                net_CO2_dict['CMU15AC-BIO demolition to 80%'],
                net_CO2_dict['CMU15AC-BIO-CCS demolition to 80%']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain demolition to 80%'],
                net_CO2_dict['CMU15AC_StrGain-CCS demolition to 80%'],
                net_CO2_dict['CMU15AC-BIO_StrGain demolition to 80%'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS demolition to 80%']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  carbonation to 80% of calcination CO$_2$'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  no further carbonation'
        entry['relative to'] = 'no further carbonation'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Additional carbonation during demolition and recovery'

    # SERVICE LIFE

        # 0% carbonated
        entry = p_dict['servicelife']

        entry['net_CO2s_bottom'] = [
            # no AC 
            [net_CO2_dict['CMU servicelife 25 years'],
                net_CO2_dict['CMU-CCS servicelife 25 years'],
                net_CO2_dict['CMU-BIO servicelife 25 years'],
                net_CO2_dict['CMU-BIO-CCS servicelife 25 years']],
            # 15%AC
            [net_CO2_dict['CMU15AC servicelife 25 years'],
                net_CO2_dict['CMU15AC-CCS servicelife 25 years'],
                net_CO2_dict['CMU15AC-BIO servicelife 25 years'],
                net_CO2_dict['CMU15AC-BIO-CCS servicelife 25 years']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain servicelife 25 years'],
                net_CO2_dict['CMU15AC_StrGain-CCS servicelife 25 years'],
                net_CO2_dict['CMU15AC-BIO_StrGain servicelife 25 years'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS servicelife 25 years']],
            ]

        # 80% carbonated
        entry['net_CO2s'] =[
            # no AC 
            [net_CO2_dict['CMU servicelife 200 years'],
                net_CO2_dict['CMU-CCS servicelife 200 years'],
                net_CO2_dict['CMU-BIO servicelife 200 years'],
                net_CO2_dict['CMU-BIO-CCS servicelife 200 years']],
            # 15%AC
            [net_CO2_dict['CMU15AC servicelife 200 years'],
                net_CO2_dict['CMU15AC-CCS servicelife 200 years'],
                net_CO2_dict['CMU15AC-BIO servicelife 200 years'],
                net_CO2_dict['CMU15AC-BIO-CCS servicelife 200 years']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain servicelife 200 years'],
                net_CO2_dict['CMU15AC_StrGain-CCS servicelife 200 years'],
                net_CO2_dict['CMU15AC-BIO_StrGain servicelife 200 years'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS servicelife 200 years']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  25 years'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  200 years'
        entry['relative to'] = '50 years'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Concrete First Use Life'

    # EXPOSURE

        entry = p_dict['exposure']

        entry['net_CO2s'] = [
            # no AC 
            [net_CO2_dict['CMU exposure outdoor, sheltered'],
                net_CO2_dict['CMU-CCS exposure outdoor, sheltered'],
                net_CO2_dict['CMU-BIO exposure outdoor, sheltered'],
                net_CO2_dict['CMU-BIO-CCS exposure outdoor, sheltered']],
            # 15%AC
            [net_CO2_dict['CMU15AC exposure outdoor, sheltered'],
                net_CO2_dict['CMU15AC-CCS exposure outdoor, sheltered'],
                net_CO2_dict['CMU15AC-BIO exposure outdoor, sheltered'],
                net_CO2_dict['CMU15AC-BIO-CCS exposure outdoor, sheltered']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain exposure outdoor, sheltered'],
                net_CO2_dict['CMU15AC_StrGain-CCS exposure outdoor, sheltered'],
                net_CO2_dict['CMU15AC-BIO_StrGain exposure outdoor, sheltered'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS exposure outdoor, sheltered']],
            ]

        entry['net_CO2s_bottom'] =[
            # no AC 
            [net_CO2_dict['CMU exposure in ground'],
                net_CO2_dict['CMU-CCS exposure in ground'],
                net_CO2_dict['CMU-BIO exposure in ground'],
                net_CO2_dict['CMU-BIO-CCS exposure in ground']],
            # 15%AC
            [net_CO2_dict['CMU15AC exposure in ground'],
                net_CO2_dict['CMU15AC-CCS exposure in ground'],
                net_CO2_dict['CMU15AC-BIO exposure in ground'],
                net_CO2_dict['CMU15AC-BIO-CCS exposure in ground']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain exposure in ground'],
                net_CO2_dict['CMU15AC_StrGain-CCS exposure in ground'],
                net_CO2_dict['CMU15AC-BIO_StrGain exposure in ground'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS exposure in ground']],
            ]

        # reference
        entry['net_CO2_ref'] =[
            # no AC
            [net_CO2_dict['CMU'],
                net_CO2_dict['CMU-CCS'],
                net_CO2_dict['CMU-BIO'],
                net_CO2_dict['CMU-BIO-CCS']],
            # 15%AC
            [net_CO2_dict['CMU15AC'],
                net_CO2_dict['CMU15AC-CCS'],
                net_CO2_dict['CMU15AC-BIO'],
                net_CO2_dict['CMU15AC-BIO-CCS']],
            # 15%AC - strength gain
            [net_CO2_dict['CMU15AC_StrGain'],
                net_CO2_dict['CMU15AC_StrGain-CCS'],
                net_CO2_dict['CMU15AC-BIO_StrGain'],
                net_CO2_dict['CMU15AC-BIO_StrGain-CCS']],
        ]

        entry['labels'] = ['Base', 'with CCS', 'with bioenergy', 'with BECCS']
        entry['line labels'] = ['no AC', '15% Cure', '15% Cure, +10% strength']
        entry['text'] = ',\n  in ground'       
        entry['bottom'] = True
        entry['bottom text'] = ',\n  outdoor sheltered'
        entry['relative to'] = '50% outdoor exposed, 50% indoor, covered'
        entry['line'] = ''
        entry['sliding'] = True
        entry['title'] = 'Concrete Exposure'

    colors = ["#002942",  '#9f4a7f', '#4a3f70', '#e5626a', '#ff9a42']
    bottom_colors = ["#7f8c9b", "#d1a3bd",  '#a29ab5', '#f9b2b2', '#ffcca0' ]
    markers = ["D", 'o', 's', '^']


    df_list = []
    names_list = []

    for k,v in p_dict.items():
        print(f"creating graph for sensitivity analysis of {k} ({id})")
        df_dict = nested_dicts(2)
        
        # absolute
        fig, ax = plt.subplots() #plt.figure()
        offset = 0
        line_count = range(len(v['line labels']))
        point_count = range(len(v['labels']))


        m_size = 8
        if v['sliding'] is True:
            lw = 6
            a = 0.4

        else:
            lw = 4
            a = 0.4

        for i in line_count:

            x_offset = [p+offset for p in point_count]
            m = markers[i]

            plt.plot(x_offset, v['net_CO2s'][i], linestyle=v['line'], marker=m, label=f"{v['line labels'][i]}{v['text']}", color=colors[i], markersize=m_size)
            if v['bottom'] is True:
                plt.plot(x_offset, v['net_CO2s_bottom'][i], linestyle=v['line'], marker=m, label=f"{v['line labels'][i]}{v['bottom text']}", color=bottom_colors[i], markersize=m_size)
                plt.vlines(x=x_offset, ymin=v['net_CO2s_bottom'][i], ymax=v['net_CO2s'][i], color=bottom_colors[i], linewidth=lw, alpha=a)
                df_dict[f"{v['line labels'][i]}{v['bottom text']}"] = v['net_CO2s_bottom'][i]
            df_dict[f"{v['line labels'][i]}{v['text']}"] = v['net_CO2s'][i]
            
            if i == len(v['net_CO2s'])-1:
                plt.plot(x_offset, v['net_CO2_ref'][i], linestyle=v['line'], marker='_', color='#ff9a42', markersize=20, label=v['relative to'])
            else:
                    plt.plot(x_offset, v['net_CO2_ref'][i], linestyle=v['line'], marker='_', color='#ff9a42', markersize=12)
            
        
            df_dict[f"{v['line labels'][i]}f{v['relative to']}"] = v['net_CO2_ref'][i]

            offset += 1/(len(v['labels']) + 0.5)

        plt.grid(True, which='both')
        idx = np.asarray([p for p in point_count])
        plt.xticks(ticks=idx, labels=v['labels'], rotation=90, fontsize="8")
        plt.subplots_adjust(right=0.6, bottom=0.3, top=0.8)
        plt.legend(bbox_to_anchor=(1.04,1), loc="upper left", fontsize="8", frameon=False)
        plt.ylabel(f"net lifecycle CO$_2$,\n kg/m$^3$ concrete")
        plt.yticks(np.arange(-100, 601, 100))
        filename = f'{id}_{k}_sens-absolute'

        plt.axhline(0, color='darkgrey')
        minor_locator = AutoMinorLocator(2)
        ax.yaxis.set_minor_locator(minor_locator)

        plt.title(v['title'])
        plt.tight_layout()

        plt.savefig(f'{figdir}/{filename}.png')
        plt.close()


        # relative
        fig, ax = plt.subplots() #plt.figure()
        offset = 0

        for i in line_count:
            x_offset = [p+offset for p in point_count]
            m = markers[i]

            net_relative = [v['net_CO2s'][i][p] - v['net_CO2_ref'][i][p] for p in point_count]
            plt.plot(x_offset, net_relative, linestyle=v['line'], marker=m, label=f"{v['line labels'][i]}{v['text']}", color=colors[i], markersize=m_size)
            if v['bottom'] is True:
                bottoms_relative = [v['net_CO2s_bottom'][i][p] - v['net_CO2_ref'][i][p] for p in point_count]
                plt.plot(x_offset, bottoms_relative, linestyle=v['line'], marker=m, label=f"{v['line labels'][i]}{v['bottom text']}", color=bottom_colors[i], markersize=m_size)
                plt.vlines(x=x_offset, ymin=bottoms_relative, ymax=net_relative, color=bottom_colors[i], linewidth=lw, alpha=a)
                        
            offset += 1/(len(v['labels']) + 0.5)

        
        plt.grid(True, which='both')
        idx = np.asarray([p for p in point_count])
        plt.xticks(ticks=idx, labels=v['labels'], rotation=90, fontsize="8")
        plt.subplots_adjust(right=0.6, bottom=0.3)
        plt.legend(bbox_to_anchor=(1.04,1), loc="upper left", fontsize="8", frameon=False)
        plt.ylabel(f"change in kg CO$_2$ per m$^3$ concrete,\nrelative to {v['relative to']}")
        plt.yticks(np.arange(-50, 51, 10))
        filename = f'{id}_{k}_sens-relative'

        plt.axhline(0, color='darkgrey')
        minor_locator = AutoMinorLocator(2)
        ax.yaxis.set_minor_locator(minor_locator)

        plt.title(v['title']+'\n')
        plt.tight_layout()

        plt.savefig(f'{figdir}/{filename}.png')
        plt.close()

        sens_df = pan.DataFrame.from_dict(df_dict, orient='index', columns=v['labels'])

        df_list.append(sens_df)
        names_list.append(k)


    with ExcelWriter(f"{dat.outdir}/{id}_sens-nets.xlsx") as writer:  
        for i, df in enumerate(df_list):
            df.to_excel(writer, sheet_name=names_list[i])

