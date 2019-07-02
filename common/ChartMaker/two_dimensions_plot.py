#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
from typing import List

import matplotlib.pyplot as plt

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
from common.PerformanceDatastructs.perf_datastruct import Perf

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class TwoDimensionsPlot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def print_graph(self, perf_list: List[Perf], output_path: pathlib.Path):
        self.logger.info(perf_list)

        plt.clf()

        TPR_list = [p.score.TPR for p in perf_list]
        TNR_list = [p.score.TNR for p in perf_list]
        FNR_list = [p.score.FNR for p in perf_list]
        FPR_list = [p.score.FPR for p in perf_list]
        ACC_list = [p.score.ACC for p in perf_list]
        F1_list = [p.score.F1 for p in perf_list]
        threshold_list = [p.threshold for p in perf_list]

        self.logger.info(f"Perf List : {perf_list}")
        self.logger.info(f"ACC List : {ACC_list}")
        self.logger.info(f"Thresholds List : {threshold_list}")

        # order :  absciss followed by ordinates
        plt.plot(threshold_list, ACC_list)
        plt.plot(threshold_list, TPR_list)
        plt.plot(threshold_list, TNR_list)
        plt.plot(threshold_list, FNR_list)
        plt.plot(threshold_list, FPR_list)
        plt.plot(threshold_list, F1_list)

        plt.legend(('Accuracy', 'True Positive Rate', 'True Negative Rate', 'False Negative rate', 'False Positive rate', 'F1'), loc='upper right')
        plt.xlabel("Threshold values [0-1]")
        plt.ylabel("Indicator value [0-1]")
        plt.title("Performance measure depending on threshold for cluster creation")

        # plt.show()
        plt.savefig(output_path / "overview.png")
        plt.clf()
        plt.cla()
        plt.close()
