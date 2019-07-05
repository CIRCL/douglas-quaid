#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

from typing import List, Set

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
import common.PerformanceDatastructs.stats_datastruct as scores
from carlhauser_server.Configuration.template_conf import JSON_parsable_Dict

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class Thresholds(JSON_parsable_Dict):
    def __init__(self, max_TPR: float = -0.001, max_FPR: float = -0.001,
                 max_FNR: float = -0.001, max_TNR: float = -0.001,
                 mean: float = -0.001):
        self.thre_upper_at_least_xpercent_TPR = max_TPR
        self.thre_upper_at_most_xpercent_FNR = max_FNR
        self.thre_below_at_least_xpercent_TNR = max_TNR
        self.thre_below_at_most_xpercent_FPR = max_FPR
        self.mean = mean

        self.percent: float = None

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' thre_upper_at_least_xpercent_TPR=', self.thre_upper_at_least_xpercent_TPR,
                                 ' thre_upper_at_most_xpercent_FNR=', self.thre_upper_at_most_xpercent_FNR,
                                 ' mean=', self.mean,
                                 ' thre_below_at_least_xpercent_TNR=', self.thre_below_at_least_xpercent_TNR,
                                 ' thre_below_at_most_xpercent_FPR=', self.thre_below_at_most_xpercent_FPR]))
