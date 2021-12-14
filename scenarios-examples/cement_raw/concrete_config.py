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

import matplotlib
matplotlib.use('TkAgg')
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
sns.set_style("whitegrid", {'font':'Helvetica'})



## DEFINE cases
##---------------------------

case = 'BASE-BIO'

m3_concrete = 1

case_list = [
        '2018-RM',
        'BASE',
        'BASE-BIO',
        '03AC',
        '03AC-BIO',
        '10AC',
        '10AC-BIO',
        ]
      
cmu_case_list = [  
        '2018-CMU',
        'CMU',
        'CMU-BIO',
        'CMU15AC',
        'CMU15AC-BIO',
        ]
         

# Concrete Weathering Properties
concrete_life = 50 # concrete lifespan
k = [1.6, 4.4]  # "k-factor" in mm/sqrt(year): 1.6 exposed to rain, 4.4 shelted from rain/indoor with cover, 6.6 indoor without cover (25-35mPa)
k_cmu = [2.7, 6.6]
A = [5,5] # exposed surface area in m2, per k
A_cmu = [9.4,9.4]
DOC = [0.85, 0.4] # degree of carbonation: 75% - sheltered from rain, 85% exposed to rain, 40% indoor, per k

EoL_calc = 0.6 # maximum calcination CO2 re-absorbed over lifetime and after end-of-life demolition

demo_CO2_LCI = 0.0089 # LCI CO2 emissions of concrete demolitions, tonne co2/tonne concrete

# Biomass Growth Properties
r = 50 

## DEFINE factories
##---------------------------  
concrete_factory = fac.Factory(chain_list_file='data/cement/factories/VOL-concrete_factory.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='concrete')

concrete_CCS_factory = fac.Factory(chain_list_file='data/cement/factories/VOL-concrete_factory-CCS.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='concrete-CCS')

factory_list = [concrete_factory, concrete_CCS_factory]
f_suffix= ["", "-CCS"] #suffix for cases from each factory to identify it
factory_names = [f.name for f in factory_list]



## DEFINE flows of interest
##---------------------------

f_kwargs=dict(
        product_qty = m3_concrete,
        upstream_outflows=['CO2', 'CO2 infrastructure'],
        upstream_inflows=['CO2 removed',],
        aggregate_flows=['CO2', 'CO2__upstream', 'CO2 infrastructure'],
        # net_flows=[('CO2', 'agg_o', 'CO2', 'agg_i')],
        )
