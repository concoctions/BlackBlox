from copy import copy
from pandas import ExcelFile
from os.path import exists

from blackblox.dataconfig import bbcfg
import blackblox.io_functions as iof
from blackblox.bb_log import get_logger



df_unit_library = None
"""dataframe of all unit process names and file locations

This data frame provides the locations of the calculations and variable tables 
for one or more unit process. Data locations for each unit process can also be 
provided invidivually when creating the a specific instance of a unit process 
class.

The index of the table contains the unique idenitifer of the unit processes
and the columns contains the location of the variable and calculation tables.
"""

df_fuels = None
"""Dataframe of information regarding different fuel types, used for combustion calculations, 
intalized from a spreadsheet including fuel name, fuel LHV, and fuel emission ratio.
Generated if 'fuel' is in bbcfg.shared_var.lookup_var_dict
"""

lookup_var_dict = None

df_upstream_outflows = None
df_upstream_inflows = None

df_downstream_outflows = None
df_downstream_inflows = None


logger = get_logger("Frames")
logger.info("Logger for frames_default.py initalized")


__is_initialized = False

def initialize():
    global __is_initialized

    if not __is_initialized:
        __attempt_initialize()
        __is_initialized = True

def __attempt_initialize():
    global df_unit_library
    global df_fuels
    global lookup_var_dict
    global df_upstream_outflows
    global df_upstream_inflows
    global df_downstream_outflows
    global df_downstream_inflows

    df_unit_library = iof.build_unit_library(
        bbcfg.paths.unit_process_library_file,
        ul_sheet=bbcfg.paths.unit_process_library_sheet
    )

    if bbcfg.shared_var.fuel_dict is not None:
        if exists(bbcfg.shared_var.fuel_dict['filepath']):
            df_fuels = iof.make_df(bbcfg.shared_var.fuel_dict['filepath'], sheet=bbcfg.shared_var.fuel_dict['sheet'])
            logger.info("df_fuels created")
        else:
            logger.info(f"ALERT: Fuels DataFrame not created (no valid filepath specified (defaults to {bbcfg.shared_var.fuel_dict['filepath']}")

    
    lookup_var_dict = copy(bbcfg.shared_var.lookup_var_dict)
    for var in lookup_var_dict:
        if 'is_fuel' in lookup_var_dict[var]:
            if lookup_var_dict[var]['is_fuel'] and df_fuels is not None:
                lookup_var_dict[var]['data_frame'] = df_fuels
        elif 'filepath' in lookup_var_dict[var]:
            if lookup_var_dict[var]['filepath']:
                if var in ['upstream outflows', 'upstream inflows', 'downstream outflows', 'downstream inflows']:
                    if 'sheet' in lookup_var_dict[var] and lookup_var_dict[var]['sheet'] is not None:
                        flows_xls = ExcelFile(lookup_var_dict[var]['filepath'])
                        if lookup_var_dict[var]['sheet'] not in flows_xls.sheet_names:
                            continue
                        else:
                            df = iof.make_df(lookup_var_dict[var]['filepath'], sheet=lookup_var_dict[var]['sheet'])
                            lookup_var_dict[var]['data_frame'] = df
                            logger.info(f"dataframe created for lookup variable {var}")

                else:
                    df = iof.make_df(lookup_var_dict[var]['filepath'], sheet=lookup_var_dict[var]['sheet'])
                    lookup_var_dict[var]['data_frame'] = df
                    logger.info(f"dataframe created for lookup variable {var}")


    if 'upstream outflows' in bbcfg.shared_var.lookup_var_dict:
        if 'data_frame' in lookup_var_dict['upstream outflows']:
            df_upstream_outflows = lookup_var_dict['upstream outflows']['data_frame']
        logger.info("df_upstream_outflows created")

    if 'upstream inflows' in bbcfg.shared_var.lookup_var_dict:
        if 'data_frame' in lookup_var_dict['upstream inflows']:
            df_upstream_inflows = lookup_var_dict['upstream inflows']['data_frame']
        logger.info("df_upstream_inflows created")

    if 'downstream outflows' in bbcfg.shared_var.lookup_var_dict:
        if 'data_frame' in lookup_var_dict['downstream outflows']:
            df_downstream_outflows = lookup_var_dict['downstream outflows']['data_frame']
        logger.info("df_downstream_outflows created")
        
    if 'downstream inflows' in bbcfg.shared_var.lookup_var_dict:
        if 'data_frame' in lookup_var_dict['downstream inflows']:
            df_downstream_inflows = lookup_var_dict['downstream inflows']['data_frame']

        logger.info("df_downstream_inflows created")
