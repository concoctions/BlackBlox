from copy import copy

import blackblox.dataconfig as dat
import blackblox.io_functions as iof
from blackblox.bb_log import get_logger


logger = get_logger("Frames")
logger.info("Logger for frames.py initalized")

df_unit_library = iof.make_df(dat.bbcfg.paths.unit_process_library_file,
                              sheet=dat.bbcfg.paths.unit_process_library_sheet)
"""dataframe of all unit process names and file locations

This data frame provides the locations of the calculations and variable tables 
for one or more unit process. Data locations for each unit process can also be 
provided invidivually when creating the a specific instance of a unit process 
class.

The index of the table contains the unique idenitifer of the unit processes
and the columns contains the location of the variable and calculation tables.
"""

df_fuels = None
if dat.bbcfg.shared_var.fuel_dict is not None:
    df_fuels = iof.make_df(dat.bbcfg.shared_var.fuel_dict['filepath'], sheet=dat.bbcfg.shared_var.fuel_dict['sheet'])
    logger.info("df_fuels created")
"""Dataframe of information regarding different fuel types, used for combustion calculations, 
intalized from a spreadsheet including fuel name, fuel LHV, and fuel emission ratio.
Generated if 'fuel' is in dat.bbcfg.shared_var.lookup_var_dict
"""

lookup_var_dict = copy(dat.bbcfg.shared_var.lookup_var_dict)
for var in lookup_var_dict:
    if 'is_fuel' in lookup_var_dict[var]:
        if lookup_var_dict[var]['is_fuel'] is True and df_fuels is not None:
            lookup_var_dict[var]['data_frame'] = df_fuels
    elif 'filepath' in lookup_var_dict[var]:
        df = iof.make_df(lookup_var_dict[var]['filepath'], sheet=lookup_var_dict[var]['sheet'])
        lookup_var_dict[var]['data_frame'] = df
        logger.info(f"dataframe created for lookup variable {var}")

df_upstream_outflows = None
if 'upstream outflows' in dat.bbcfg.shared_var.lookup_var_dict:
    df_upstream_outflows = iof.make_df(dat.bbcfg.shared_var.lookup_var_dict['upstream outflows']['filepath'],
                                       sheet=dat.bbcfg.shared_var.lookup_var_dict['upstream outflows']['sheet'])
    logger.info("df_upstream_outflows created")

df_upstream_inflows = None
if 'upstream inflows' in dat.bbcfg.shared_var.lookup_var_dict:
    df_upstream_inflows = iof.make_df(dat.bbcfg.shared_var.lookup_var_dict['upstream inflows']['filepath'],
                                      sheet=dat.bbcfg.shared_var.lookup_var_dict['upstream inflows']['sheet'])
    logger.info("df_upstream_inflows created")

df_downstream_outflows = None
if 'downstream outflows' in dat.bbcfg.shared_var.lookup_var_dict:
    df_downstream_outflows = iof.make_df(dat.bbcfg.shared_var.lookup_var_dict['downstream outflows']['filepath'],
                                         sheet=dat.bbcfg.shared_var.lookup_var_dict['downstream outflows']['sheet'])
    logger.info("df_downstream_outflows created")

df_downstream_inflows = None
if 'downstream inflows' in dat.bbcfg.shared_var.lookup_var_dict:
    df_downstream_inflows = iof.make_df(dat.bbcfg.shared_var.lookup_var_dict['downstream inflows']['filepath'],
                                        sheet=dat.bbcfg.shared_var.lookup_var_dict['downstream inflows']['sheet'])
    logger.info("df_downstream_inflows created")
