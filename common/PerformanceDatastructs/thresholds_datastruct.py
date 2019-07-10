#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
from carlhauser_server.Configuration.template_conf import JSON_parsable_Dict
from carlhauser_server.Configuration.algo_conf import Algo_conf

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# TODO : Conf file to export ! :D

class OLD_Thresholds(JSON_parsable_Dict):
    def __init__(self):
        self.thre_upper_at_least_xpercent_TPR: float = None
        self.thre_upper_at_most_xpercent_FNR: float = None
        self.thre_below_at_least_xpercent_TNR: float = None
        self.thre_below_at_most_xpercent_FPR: float = None
        self.mean: float = None

    def export_to_Algo_Conf_aggressive(self, input_Algo_Conf: Algo_conf) -> Algo_conf:
        # Overwrite parameter of the algorithm configuration
        # to apply the thresholds it contains to this algorithm configuration
        # AGGRESSIVE = Work on negative rate

        input_Algo_Conf.threshold_no = self.thre_upper_at_most_xpercent_FNR
        input_Algo_Conf.threshold_maybe = self.thre_below_at_least_xpercent_TNR

        return input_Algo_Conf

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
