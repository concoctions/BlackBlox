from pathlib import Path
import sys
sys.path.append('/Users/Tanzer/GitHub/BlackBlox/')

from copy import deepcopy
from datetime import datetime
import blackblox.dataconfig as dat
import blackblox.factory as fac
import blackblox.industry as ind

dat.outdir = f'{dat.outdir}/{dat.time}'
Path(dat.outdir).mkdir(parents=True, exist_ok=True) 
dat.user_data = {"name": "S.E. Tanzer",
             "affiliation": "Delft Univeristy of Technology, Faculty of Technology, Policy, and Management",
             "project": "D-LCA of BECCS and Accelerated Carbonation in Concrete Production",
}
dat.default_scenario = "BASE"
dat.default_emissions = ["CO2__bio", "CO2__fossil", "contrib_CO2__bio-annual", "contrib_CO2__bio-long"]

import concrete_config as conf
from cases import base_cases
from singlevar_sens import multi_sens
from sens_exposure import sens_exposure
from sens_demo import sens_demo
from sens_rotation import sens_rotation
from sens_servicelife import sens_servicelife
from sens_graphs import sens_graphs

orig_outdir = dat.outdir

# origin_f = deepcopy(conf.factory_list)
# origin_s = deepcopy(conf.f_suffix)

# DAC_factory = fac.Factory(chain_list_file='data/cement/factories/VOL-concrete_factory-DACCS.xlsx',
#                     chain_list_sheet='chains', 
#                     connections_sheet='connections', 
#                     name='concrete w DAC AC')

# fluegasAC_factory = fac.Factory(chain_list_file='data/cement/factories/VOL-concrete_factory-flueCO2.xlsx',
#                     chain_list_sheet='chains', 
#                     connections_sheet='connections', 
#                     name='flue gas AC')

# fluegasAC_CCS_factory = fac.Factory(chain_list_file='data/cement/factories/VOL-concrete_factory-CCS-flueCO2.xlsx',
#                     chain_list_sheet='chains', 
#                     connections_sheet='connections', 
#                     name='flue gas AC-CCS')

# ownCO2_CCS_factory = fac.Factory(chain_list_file='data/cement/factories/VOL-concrete_factory-CCS-ownCO2AC.xlsx',
#                     chain_list_sheet='chains', 
#                     connections_sheet='connections', 
#                     name='own CO2 AC-CCS')

# origin_f.extend([ DAC_factory, fluegasAC_factory, fluegasAC_CCS_factory, ownCO2_CCS_factory,])
# origin_s.extend(['-DAC', '-flue', '-CCS-flue', '-CCS-ownCO2' ])
# origin_n = [f.name for f in origin_f ]



print(f'\n>--START--->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{datetime.now().strftime("%H%M")}\n')


# #### 30MPA CONCRETE ####

# print('ORDINARY PORTLAND CONCRETE')

# print('>>>running base cases')


# # 2018-2050 base cases
# case_list = [
#         'BASE',
#         'BASE-BIO',
#         '2050-RM',
#         '2050-RM-BIO',
#         '2050-RM-opt', 
#         '2050-RM-BIO-opt',
# ]

# order = [ 'BASE', 'BASE-BIO', 'BASE-CCS',  'BASE-BIO-CCS',
#         '2050-RM', '2050-RM-BIO', '2050-RM-CCS',  '2050-RM-BIO-CCS',
#          '2050-RM-opt', '2050-RM-BIO-opt','2050-RM-opt-CCS','2050-RM-BIO-opt-CCS', ]

# case_labels = [ 'Current, Benchmark', 'Current, Benchmark\nwith bioenergy', 'Current, Benchmark,\nwith CCS','Current, Benchmark\n with BECCS',
#         'Future, conservative', 'Future, conservative,\n with full bioenergy', 'Future conservative,\nwith CCS', 'Future, conservative,\nwith BECCS', 
#         'Future, optimistic',  'Future, optimsitic,\n with full bioenergy', 'Future, optimisitc,\nwith CCS', 'Future, optimsitic,\nwith full BECCS',]

# id_groups = ['BASE', 'None', 'opt']
# group_names = ['Current, Benchmark', 'Future, Conservative', 'Future, Optimistic']

# mpa30_CO2_dict, rm_net_dict = base_cases(case_list, order=order, case_labels=case_labels, 
#                                 id_groups=id_groups, group_names=group_names, id='30mpa-overtime', )


# # 2018-2050 base cases
# case_list = [
#         '2018-RM',
#         'BASE',
#         'BASE-BIO',
#         '2050-RM',
#         '2050-RM-BIO',
#         '2050-RM-opt', 
#         '2050-RM-BIO-opt',
# ]

# order = [ '2018-RM', 
#         'BASE', 'BASE-BIO', 'BASE-CCS',  'BASE-BIO-CCS',
#         '2050-RM', '2050-RM-BIO', '2050-RM-CCS',  '2050-RM-BIO-CCS',
#          '2050-RM-opt', '2050-RM-BIO-opt','2050-RM-opt-CCS','2050-RM-BIO-opt-CCS', ]

# case_labels = ['Current, Average', 
#         'Current, Benchmark', 'Current, Benchmark\nwith bioenergy', 'Current, Benchmark,\nwith CCS','Current, Benchmark\n with BECCS',
#         'Future, conservative', 'Future, conservative,\n with full bioenergy', 'Future conservative,\nwith CCS', 'Future, conservative,\nwith BECCS', 
#         'Future, optimistic',  'Future, optimsitic,\n with full bioenergy', 'Future, optimisitc,\nwith CCS', 'Future, optimsitic,\nwith full BECCS',]

# id_groups = ['2018', 'BASE', 'None', 'opt']
# group_names = ['Current, Average', 'Current, Benchmark', 'Future, Conservative', 'Future, Optimistic']

# mpa30_CO2_dict, rm_net_dict = base_cases(case_list, order=order, case_labels=case_labels, 
#                                 id_groups=id_groups, group_names=group_names, id='30mpa-mixed', )

# # AC-cases only
# case_list = ['BASE', '03AC', '10AC', '10AC_StrGain']
# order = ['BASE', '03AC', '10AC', '10AC_StrGain']
# case_labels =  ['No AC', '0.3% CO$_2$ injection', '10% CO$_2$ curing\no strength gain', '10% CO$_2$ curing\n 10% strength gain']
        
# mpa30_CO2_more, mpa30_net_more = base_cases(case_list, order=order, case_labels=case_labels, factory_list=[conf.concrete_factory], id='30mpa-AConly',)

# mpa30_CO2_dict.update(mpa30_CO2_more)
# rm_net_dict.update(mpa30_net_more)


# # AC Strength and CO2 origin
# print('>>>running sensitivity analyses: CO2 origin')

# dat.outdir = f'{orig_outdir}/AC CO2 source'
# Path(dat.outdir).mkdir(parents=True, exist_ok=True) 

# mpa30_CO2_more, mpa30_net_more = base_cases(['10AC', '10AC_bioAC', '10AC_StrGain'], 
#                                               factory_list=origin_f, f_suffix=origin_s, factory_names=origin_n, id='30mpa-CO2',)
# mpa30_CO2_dict.update(mpa30_CO2_more)
# rm_net_dict.update(mpa30_net_more)

# dat.outdir = orig_outdir

# # other cases needed for sensitivity analysis

# id_groups = ['not _', ['10AC_StrGain','10AC-BIO_StrGain'], '2050']
# group_names = ['Current, Bnechmark', 'Current, Benchmark, 10% strength gain', 'Future, optimistc', 'Future, optimistic, 10% strength gain']

# mpa30_CO2_more, mpa30_net_more = base_cases(['03AC', '03AC-BIO', '10AC', '10AC-BIO', '10AC_StrGain','10AC-BIO_StrGain', '2050-10AC-opt_StrGain', '2050-10AC-BIO-opt_StrGain',], 
#                                 id_groups=id_groups, group_names=group_names, id='30mpa_str', )
# mpa30_CO2_dict.update(mpa30_CO2_more)
# rm_net_dict.update(mpa30_net_more)


# # sensitivity analyses

# case_list = [
#         'BASE',
#         'BASE-BIO',
#         '10AC_StrGain',
#         '10AC-BIO_StrGain',
# ]

# print('>>>running sensitivity analyses: electricity, transport, kiln eff, CO2 Cap Eff, recycled aggregate')
# mpa30_net_more = multi_sens(case_list, id='30mpa-base', fast=True)
# rm_net_dict.update(mpa30_net_more)


# case_list = [
#         'BASE',
#         'BASE-BIO',
#         '03AC', 
#         '03AC-BIO',
#         '10AC', 
#         '10AC-BIO',
# ]

# print('>>>running sensitivity analyses: electricity, transport, kiln eff, CO2 Cap Eff, recycled aggregate')
# mpa30_net_more = multi_sens(case_list, id='30mpa-ac', fast=True)
# rm_net_dict.update(mpa30_net_more)

# case_list = [
#         '2018-RM',
#         '2050-RM',
#         '2050-RM-BIO',
#         '2050-RM-opt', 
#         '2050-RM-BIO-opt',
# ]

# print('>>>running sensitivity analyses: electricity, transport, kiln eff, CO2 Cap Eff, recycled aggregate')
# mpa30_net_more = multi_sens(case_list, id='30mpa-2050', fast=True)
# rm_net_dict.update(mpa30_net_more)


# print('>>>running sensitivity analyses: concrete exposure')
# mpa30_net_more = mpa30_exposure_net = sens_exposure(deepcopy(mpa30_CO2_dict), id='30mpa')
# rm_net_dict.update(mpa30_net_more)


# print('>>>running sensitivity analyses: concrete service life')
# mpa30_net_more = mpa30_exposure_net = sens_servicelife(deepcopy(mpa30_CO2_dict), case_list=['BASE', 'BASE-BIO-CCS', '10AC', '10AC_StrGain'], id='30mpa')
# rm_net_dict.update(mpa30_net_more)


# print('>>>running sensitivity analyses: concrete demolition')
# mpa30_net_more = sens_demo(deepcopy(mpa30_CO2_dict), case_list=['BASE', 'BASE-BIO-CCS'], id='30mpa')
# rm_net_dict.update(mpa30_net_more)


# print('>>>running sensitivity analyses: biomass rotation')
# mpa30_net_more = sens_rotation(deepcopy(mpa30_CO2_dict), case_list=['BASE-BIO', '2050-RM-BIO-opt',], id='30mpa')
# rm_net_dict.update(mpa30_net_more)

# print('>>>creating sensitivity analysis graphs')
# sens_graphs(rm_net_dict, id='30mpa')


# #### CONCRETE MASONRY UNITS ####

# print('CONCRETE MASONRY UNITS')

# print('>>>running base cases')

# case_list = [  
#         '2018-CMU',
#         'CMU',
#         'CMU-BIO',
#         '2050-CMU', 
#         '2050-CMU-BIO', 
#         '2050-CMU-opt',
#         '2050-CMU-BIO-opt'
#         ]

# order = ['2018-CMU', 
#         'CMU', 'CMU-BIO', 'CMU-CCS', 'CMU-BIO-CCS',
#         '2050-CMU', '2050-CMU-BIO', '2050-CMU-CCS', '2050-CMU-BIO-CCS',
#          '2050-CMU-opt', '2050-CMU-BIO-opt', '2050-CMU-opt-CCS',  '2050-CMU-BIO-opt-CCS', ]

# case_labels = ['Current, Average', 
#         'Current, Benchmark', 'Current, Benchmark\nwith bioenergy', 'Current, Benchmark,\nwith CCS','Current, Benchmark\n with BECCS',
#         'Future, conservative',  'Future, conservative,\n with full bioenergy', 'Future conservative,\nwith CCS', 'Future, conservative,\nwith  full BECCS', 
#         'Future, optimistic',  'Future, optimsitic,\n with full bioenergy', 'Future, optimisitc,\nwith CCS',  'Future, optimsitic,\nwith full BECCS',]

# id_groups = [['2018-CMU', '2018-CMU-CCS',], ['CMU', 'CMU-BIO', 'CMU-CCS',  'CMU-BIO-CCS',], '2050 not opt', 'opt']
# group_names = ['Current, Average', 'Current, Benchmark', 'Future, Conservative', 'Future, Optimistic']

# cmu_CO2_dict, cmu_net_dict = base_cases(case_list=case_list, order=order, case_labels=case_labels,
#                                         id_groups=id_groups, group_names=group_names, id='cmu-mixed', )

# # AC Cases only

# case_list = ['CMU', 'CMU15AC', 'CMU15AC_StrGain',]
# order = ['CMU', 'CMU15AC', 'CMU15AC_StrGain']
# case_labels =  ['No AC', '15% CO$_2$ curing\no strength gain', '15% CO$_2$ curing\n 10% strength gain']
 
# cmu_CO2_more, cmu_net_more = base_cases(case_list, order=order, case_labels=case_labels, factory_list=[conf.concrete_factory], id='cmu-AConly',)
# cmu_CO2_dict.update(cmu_CO2_more)
# cmu_net_dict.update(cmu_net_more)


# # CO2 Origin and Strength

# print('>>>running sensitivity analyses: CO2 origin')

# dat.outdir = f'{orig_outdir}/AC CO2 source'
# Path(dat.outdir).mkdir(parents=True, exist_ok=True) 

# cmu_CO2_more, cmu_net_more  = base_cases(['CMU15AC', 'CMU15AC_bioAC', 'CMU15AC_StrGain'], 
#                                         factory_list=origin_f, f_suffix=origin_s, factory_names=origin_n, id='cmu-CO2')
# cmu_CO2_dict.update(cmu_CO2_more)
# cmu_net_dict.update(cmu_net_more)

# dat.outdir = orig_outdir


# # other cases needed for sensitivity analysis

# id_groups = ['not _', ['CMU15AC_StrGain','CMU15AC-BIO_StrGain'], '2050']
# group_names = ['Current, Benchmark', 'Current, Benchmark, 10% strength gain', 'Future, optimistc', 'Future, optimistic, 10% strength gain']

# cmu_CO2_more, cmu_net_more= base_cases(['CMU', 'CMU15AC', 'CMU15AC-BIO', 'CMU15AC_StrGain', 'CMU15AC-BIO_StrGain', '2050-CMU', '2050-CMU-BIO', '2050-CMU-opt', '2050-CMU-BIO-opt', '2050-CMU-opt_StrGain',  '2050-CMU15AC-BIO-opt_StrGain'], 
#                                         id_groups=id_groups, group_names=group_names, id='cmu_str', )
# cmu_CO2_dict.update(cmu_CO2_more)
# cmu_net_dict.update(cmu_net_more)


# print('>>>running sensitivity analyses: electricity, transport, kiln eff, CO2 Cap Eff, recycled aggregate')

# case_list = [  
#         '2018-CMU',
#         'CMU',
#         'CMU-BIO',
#         'CMU15AC',
#         'CMU15AC-BIO',
#         'CMU15AC_StrGain',
#         'CMU15AC-BIO_StrGain'
#         ]

# cmu_net_more = multi_sens(case_list, id='cmu', fast=True)
# cmu_net_dict.update(cmu_net_more)

# print('>>>running sensitivity analyses: concrete exposure')

# cmu_net_more = sens_exposure(deepcopy(cmu_CO2_dict), id='cmu')
# cmu_net_dict.update(cmu_net_more)

# print('>>>running sensitivity analyses: concrete service life')

# cmu_net_more = sens_servicelife(deepcopy(cmu_CO2_dict), case_list=['CMU', 'CMU-BIO-CCS'], id='cmu',)
# cmu_net_dict.update(cmu_net_more)

# print('>>>running sensitivity analyses: concrete demolition')

# cmu_net_more = sens_demo(deepcopy(cmu_CO2_dict), case_list=['CMU', 'CMU-BIO-CCS'], id='cmu')
# cmu_net_dict.update(cmu_net_more)

# print('>>>running sensitivity analyses: biomass rotation')

# cmu_net_more = sens_rotation(deepcopy(cmu_CO2_dict), case_list=['CMU-BIO', '2050-CMU-BIO-opt'], id='cmu')
# cmu_net_dict.update(cmu_net_more)

# print('>>>creating sensitivity analysis graphs')
# sens_graphs(cmu_net_dict, id='cmu')



# print('>>>creating additional graphs')

# # CASES with both OPC and CMU ###

# case_list = ['BASE', '03AC', 
#             '10AC', '10AC_StrGain', 
#              'CMU', 'CMU15AC', 'CMU15AC_StrGain',]

# order = ['BASE', '03AC', 
#         '10AC', '10AC_StrGain', 
#         'CMU', 'CMU15AC', 'CMU15AC_StrGain']
        
# case_labels =  ['OPC,\nNo AC', 'OPC,\n0.3% CO$_2$ injection', 
#                 'OPC,\n10% CO$_2$ curing\no strength gain', 'OPC,\n10% CO$_2$ curing\n 10% strength gain',
#                 'CMUs,\nNo AC', 'CMUs,\n15% CO$_2$ curing\no strength gain', 'CMUs,\n15% CO$_2$ curing\n 10% strength gain']


# id_groups = [['BASE', 'CMU',], ['10AC', 'CMU15AC', ], ['10AC_StrGain', 'CMU15AC_StrGain']]
# group_names = ['No Accerated Carbonation', 'CO$_2$ curing,', 'CO$_2$ curing 10% strength gain', ]

# base_cases(case_list,  order=order, case_labels=case_labels, factory_list=[conf.concrete_factory], id_groups=id_groups, group_names=group_names, id='double-AConly', )     



# case_list = [
#         # '2018-RM',
#         'BASE',
#         'BASE-BIO',
#         '2050-RM',
#         '2050-RM-BIO',
#         '2050-RM-opt', 
#         '2050-RM-BIO-opt',
#         # '2018-CMU',
#         'CMU',
#         'CMU-BIO',
#         '2050-CMU',
#         '2050-CMU-BIO',
#         '2050-CMU-opt',
#         '2050-CMU-BIO-opt', 
#         ]


# order = [ 
#         # '2018-RM', '2018-RM-CCS',
#         'BASE', 'BASE-BIO', 'BASE-CCS',  'BASE-BIO-CCS',
#         '2050-RM', '2050-RM-BIO', '2050-RM-CCS',  '2050-RM-BIO-CCS',
#         '2050-RM-opt', '2050-RM-BIO-opt','2050-RM-opt-CCS','2050-RM-BIO-opt-CCS', 
#         # '2018-CMU', '2018-CMU-CCS',
#         'CMU', 'CMU-BIO', 'CMU-CCS',  'CMU-BIO-CCS',
#         '2050-CMU', '2050-CMU-BIO', '2050-CMU-CCS', '2050-CMU-BIO-CCS',
#         '2050-CMU-opt', '2050-CMU-opt-CCS', '2050-CMU-BIO-opt', '2050-CMU-BIO-opt-CCS', ]

# case_labels = [
#         # 'OPC, Current, Average', 'OPC, Current, Average\nwith CCS',
#         'OPC, Current, Benchmark', 'OPC, Current, Benchmark\nwith bioenergy', 'OPC, Current, Benchmark,\nwith CCS','OPC, Current, Benchmark\n with BECCS',
#         'OPC, Future, conservative',  'OPC, Future, conservative,\n with full bioenergy', 'OPC, Future conservative,\nwith CCS', 'OPC, Future, conservative,\nwith full BECCS', 
#         'OPC, Future, optimistic',  'OPC, Future, optimsitic,\n with full bioenergy', 'OPC, Future, optimisitc,\nwith CCS', 'OPC, Future, optimistic,\nwith full  BECCS',
#         # 'CMUs, Current, Average', 'CMUs, Current, Average\nwith CCS',
#         'CMUs, Current, Benchmark', 'CMUs, Current, Benchmark\nwith bioenergy', 'CMUs, Current, Benchmark,\nwith CCS','CMUs, Current, Benchmark\n with BECCS',
#         'CMUs, Future, conservative',  'CMUs, Future, conservative,\n with bioenergy', 'CMUs, Future conservative,\nwith CCS', 'CMUs, Future, conservative,\nwith full BECCS', 
#         'CMUs, Future, optimistic',  'CMUs, Future, optimsitic,\n with full bioenergy', 'CMUs, Future, optimisitc,\nwith CCS', 'CMUs, Future, optimsitic,\nwith full BECCS',]


# id_groups = [ 
#         ['BASE', 'BASE-BIO', 'BASE-CCS',  'BASE-BIO-CCS', 'CMU', 'CMU-BIO', 'CMU-CCS',  'CMU-BIO-CCS', ],
#         ['2050-RM', '2050-RM-BIO', '2050-RM-CCS',  '2050-RM-BIO-CCS','2050-CMU', '2050-CMU-BIO', '2050-CMU-CCS', '2050-CMU-BIO-CCS',],
#         ['2050-RM-opt', '2050-RM-BIO-opt','2050-RM-opt-CCS','2050-RM-BIO-opt-CCS', '2050-CMU-opt', '2050-CMU-opt-CCS', '2050-CMU-BIO-opt', '2050-CMU-BIO-opt-CCS',]
# ]

# group_names = ['Current, Benchmark', 'Future, Conservative', 'Future, Optimistic']

# base_cases(case_list, order=order, case_labels=case_labels, id_groups=id_groups, group_names=group_names, id='double' ) 

# #

# case_list = [
#         'BASE',
#         'BASE-BIO',
#         '03AC',
#         '03AC-BIO',
#         '10AC',
#         '10AC-BIO',
#         ]
      
# order = ['BASE', '03AC', '10AC',   
#                 'BASE-CCS', '03AC-CCS', '10AC-CCS',  
#                 'BASE-BIO', '03AC-BIO', '10AC-BIO',  
#                 'BASE-BIO-CCS', '03AC-BIO-CCS', '10AC-BIO-CCS' ]

# case_labels = ['No AC', '0.3% CO$_2$ injection', '10% CO$_2$ curing',  
#                     'No AC,\nCCS', '0.3% CO$_2$ injection,\nCCS', '10% CO$_2$ curing,\nCCS',    
#                     'No AC,\nBioenergy', '0.3% CO$_2$ injection,\nBioenergy', '10% CO$_2$ curing,\nBioenergy', 
#                     'No AC,\nBECCS', '0.3% CO$_2$ injection,\nBECCS', '10% CO$_2$ curing,\nBECCS', ]

# base_cases(case_list, order=order, case_labels=case_labels, id='30mpa', )

# #

# case_list = [  
#         'CMU',
#         'CMU-BIO',    
#         'CMU15AC',
#         'CMU15AC-BIO',
#         ]
# order = ['CMU', 'CMU15AC',
# 'CMU-CCS', 'CMU15AC-CCS',   
# 'CMU-BIO', 'CMU15AC-BIO',  
# 'CMU-BIO-CCS', 'CMU15AC-BIO-CCS',  ]

# case_labels = ['No AC', '15% CO$_2$ curing',
# 'No AC,\nCCS', '15% CO$_2$ curing,\nCCS',        
# 'No AC,\nBioenergy', '15% CO$_2$ curing,\nBioenergy',    
# 'No AC,\nBECCS', '15% CO$_2$ curing,\nBECCS' ]  

# base_cases(case_list, order=order, case_labels=case_labels, id='cmu', )




# case_list = [
#         '2018-RM',
#         'BASE',
#         'BASE-BIO',
#         '03AC',
#         '03AC-BIO', 
#         '10AC', 
#         '10AC-BIO', 
#         '10AC_StrGain',
#         '10AC-BIO_StrGain',
#         '2050-RM',
#         '2050-RM-BIO',
#         '2050-RM-opt', 
#         '2050-RM-BIO-opt',
#         '2018-CMU',
#         'CMU',
#         'CMU-BIO',
#         'CMU15AC',
#         'CMU15AC-BIO', 
#         'CMU15AC_StrGain',
#         'CMU15AC-BIO_StrGain',
#         '2050-CMU',
#         '2050-CMU-BIO',
#         '2050-CMU-opt',
#         '2050-CMU-BIO-opt', 
#         ]


# base_cases(case_list, id='allcases-double' ) 


# Cement Only


case_list = [
        '2018-RM',
        'BASE',
        'BASE-BIO',
        '2050-RM',
        '2050-RM-BIO',
        '2050-RM-opt', 
        '2050-RM-BIO-opt',
]

order = [ '2018-RM', '2018-RM-CCS',
        'BASE', 'BASE-BIO', 'BASE-CCS',  'BASE-BIO-CCS',
        '2050-RM', '2050-RM-BIO', '2050-RM-CCS',  '2050-RM-BIO-CCS',
         '2050-RM-opt', '2050-RM-BIO-opt','2050-RM-opt-CCS','2050-RM-BIO-opt-CCS', ]

case_labels = ['Current, Average', 'Current, Average\nwith CCS',
        'Current, Benchmark', 'Current, Benchmark\nwith bioenergy', 'Current, Benchmark,\nwith CCS','Current, Benchmark\n with BECCS',
        'Future, conservative',  'Future, conservative,\n with full bioenergy', 'Future conservative,\nwith CCS', 'Future, conservative,\nwith  full BECCS', 
        'Future, optimistic',  'Future, optimsitic,\n with full bioenergy', 'Future, optimisitc,\nwith CCS', 'Future, optimsitic,\nwith full BECCS',]

id_groups = ['2018', 'BASE', 'None', 'opt']
group_names = ['Current, Average', 'Current, Benchmark', 'Future, Conservative', 'Future, Optimistic']

f_list = [fac.Factory(chain_list_file='data/cement/factories/cement_factory.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='cement'),
                    fac.Factory(chain_list_file='data/cement/factories/cement_factory-CCS.xlsx',
                    chain_list_sheet='chains', 
                    connections_sheet='connections', 
                    name='cement-CCS')]

f_suffix= ["", "-CCS"] #suffix for cases from each factory to identify it
f_names = [f.name for f in f_list]

base_cases(case_list=case_list, order=order, case_labels=case_labels, id_groups=id_groups, group_names=group_names,
                        factory_list=f_list, f_suffix=f_suffix, factory_names=f_names, id='cement')


# compare cement by qty for product:

# i_kwargs = dict(factory_list_file='data/cement/cement_qty_compare.xlsx',
#                 factory_list_sheet='Factory List', 
#                 name='cement compare qty')

# industry = ind.Industry(**i_kwargs)

# industry.balance(production_data_sheet='2018',
#                 write_to_xls=True, 
#                 upstream_outflows=['CO2', 'CO2 infrastructure'],
#                 upstream_inflows=['CO2 removed',],
#                 aggregate_flows=['CO2', 'CO2__upstream', 'CO2 infrastructure'])


print(f'\n{datetime.now().strftime("%H%M")}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<--END---<\n')




