# -*- coding: utf-8 -*-
""" Logger generatior

This module defines the logging system used in BlackBlox.py.

Created using the recipe from
https://gist.github.com/nguyenkims/e92df0f8bd49973f0c94bddf36ed7fd0

"""
import logging
import platform
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime

Path("logs").mkdir(parents=True, exist_ok=True) 

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
LOG_FILE = Path("logs/BlackBlox.log")


def get_file_handler():
    """Chooses a file handler based on the operating system of the user
    Windows (7, 10) doesn't like the rotating file handler,  so if the user OS is 
    Windows, a static file handler is used, but the current date is suffixed to 
    the filename. However, if the program is run over multiple days, the log file
    name will  not automatically switch.
    """
    if platform.system() is 'Windows':
        file_handler = logging.FileHandler(f"{LOG_FILE}_{datetime.now().strftime('%Y-%m-%d')}")
    else:
        file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')

    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # logger.addHandler(get_console_handler()) #uncomment to output log to console
    logger.addHandler(get_file_handler())
    logger.propagate = False

    return logger
