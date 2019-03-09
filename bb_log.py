# -*- coding: utf-8 -*-
""" Logger generatior

This module defines the logging system used in BlackBlox.py.

Created using the recipe from
https://gist.github.com/nguyenkims/e92df0f8bd49973f0c94bddf36ed7fd0

"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
Path("logs").mkdir(parents=True, exist_ok=True) 
LOG_FILE = Path("logs/BlackBlox.log")

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_file_handler():
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