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
from common.PerformanceDatastructs.thresholds_datastruct import Thresholds

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class TwoDimensionsPlot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # ========================= EXTERNAL USAGE =========================

    def print_graph(self, perf_list: List[Perf], output_path: pathlib.Path):
        # Print a graph with the TPR,TNR,FPR,FNR ... on one unique chart

        output_file = output_path / "overview.png"
        self.logger.debug(f"Computing and saving graph with threshold at {output_file}")

        plt.clf()
        legend = self.plot_perf_list(perf_list)
        self.add_meta(legend)
        self.save_fig(output_path=output_file)

    def print_graph_with_thresholds(self, perf_list: List[Perf], thresholds_handler: Thresholds, output_path: pathlib.Path):
        # Print a graph with the TPR,TNR,FPR,FNR ... with thresholds provided on one unique chart

        output_file = output_path / "overview_with_thresholds.png"
        self.logger.debug(f"Computing and saving graph with threshold at {output_file}")

        plt.clf()
        legend = self.plot_perf_list(perf_list)
        legend += self.plot_thresholds(thresholds_handler)
        self.add_meta(legend)

        self.save_fig(output_path=output_file)

    # ========================= INTERNAL (FACTORIZATION PURPOSES) =========================
    def plot_perf_list(self, perf_list: List[Perf]):
        self.logger.info(perf_list)

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

        legend = ('Accuracy', 'True Positive Rate', 'True Negative Rate', 'False Negative rate', 'False Positive rate', 'F1')
        return legend

    def add_meta(self, legend):

        plt.legend(legend , loc='upper right')
        plt.xlabel("Threshold values [0-1]")
        plt.ylabel("Indicator value [0-1]")
        plt.title("Performance measure depending on threshold for cluster creation")

    def plot_thresholds(self, thresholds_handler: Thresholds):
        self.logger.info(thresholds_handler)

        # x coordinates for the lines
        xcoords = [thresholds_handler.max_TPR, thresholds_handler.mean, thresholds_handler.max_FPR]
        # colors for the lines
        colors = ['b', 'y', 'r']
        labels = ['TruePositiveRate threshold - Yes to Maybe', ' Mean threshold if full auto', 'TruePositiveRate threshold - Maybe to No']

        for xc, l, c in zip(xcoords, labels, colors):
            plt.axvline(x=xc, label=l + 'x = {}'.format(xc), c=c)

        legend = tuple(labels)
        return legend

    def save_fig(self, output_path: pathlib.Path):
        # plt.show()
        plt.savefig(output_path)
        plt.clf()
        plt.cla()
        plt.close()
