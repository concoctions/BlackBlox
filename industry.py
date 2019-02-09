import pandas as pan
from collections import defaultdict
from graphviz import Digraph
from datetime import datetime

from bb_log import get_logger

import io_functions as iof
import dataconfig as dat
import factory as fac


logger = get_logger("Industry")

class Industry:
    """
    Industries are made up of one or more factories, and are balanced on one or more
    factory products. Factories within an industry can run with different scenario
    data. Industries can change over time.
    """

    def __init__(self, industry_data, name='Industry'):

    def initalize(self)
    
    def run_scenarios(self, scenario_list=[default_scenario]):

    def evolve(self, evolution_data, sheets=None):
        """Runs a scen
        evolution_data (string or list of strings)
        sheets (string or list of strings)
        """

