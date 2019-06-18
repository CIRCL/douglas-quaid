#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time
import traceback
from typing import List
import matplotlib.pyplot as plt

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
import carlhauser_server.core as core

import carlhauser_client.EvaluationTools.ClassificationQuality.classification_quality_evaluator as evaluator
import carlhauser_client.EvaluationTools.ClassificationQuality.stats_datastruct as scores

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


class Perf():
    def __init__(self, score: scores.Stats_datastruct, threshold: float):
        self.score = score
        self.threshold = threshold


# ==================== ------ LAUNCHER ------- ====================
class ParameterExplorer():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # TMP
        self.server_launcher = None
        self.client_launcher = None

    def launch(self):
        # ========= INPUTS =========
        # Input files folder
        image_folder = get_homedir() / "datasets" / "MINI_DATASET"
        # Ground truth file
        gt = get_homedir() / "datasets" / "MINI_DATASET_VISJS.json"
        # Output general folder
        output_folder = get_homedir() / "datasets" / "OUTPUT"
        output_folder.mkdir(parents=True, exist_ok=True)

        # ========= GOAL =========
        perfs = []

        iterations_limit = 50  # 50  # Or nb of iteration if complete exploration

        max_threshold = 1
        min_threshold = 0

        # ========= CONFIGURATION CHOSING =========

        for i in range(iterations_limit):

            # Computing the new threshold
            curr_threshold = i * ((max_threshold - min_threshold) / iterations_limit)
            self.logger.info(f"Current threshold computation : {curr_threshold}")

            # Choose a configuration
            # Put configuration in place
            if self.server_launcher is not None:
                del self.server_launcher
            self.server_launcher = core.launcher_handler()
            self.server_launcher.di_conf.MAX_DIST_FOR_NEW_CLUSTER = curr_threshold

            ''' 
            # TODO : Go in the "right" direction. 
            # while the score is changing
            while(curr_round_score > last_round_score and i < iterations_limit):
    
                # Good direction, continue
                if curr_round_score > last_round_score :
    
    
                    continue
                # Bad direction, go "back"
                else :
                    continue
    
                i+=1
            '''

            # Create output folder for this configuration
            tmp_output = output_folder / ''.join([str(curr_threshold), "_threshold"])
            tmp_output.mkdir(parents=True, exist_ok=True)

            # ========= CONFIGURATION LAUNCH =========

            # Launch Server
            self.server_launcher.launch()
            time.sleep(2)

            # Launch client tester
            self.client_launcher = evaluator.ClassificationQualityEvaluator()
            perf_overview = self.client_launcher.launch(image_folder, gt, tmp_output)
            self.logger.warning(f"Perf overview added : {perf_overview}")

            perfs.append(Perf(perf_overview, curr_threshold))

            # Wait for client end

            # ========= TIDY UP FOR NEXT ROUND =========

            # Flush server
            self.server_launcher.flush_db()

            # Shutdown server
            self.server_launcher.stop()

            # Wait for shutdown (wait for workers to shutdown, usually longer than db)
            while not self.server_launcher.check_worker():
                time.sleep(1)  # Enough ?
                self.logger.warning("Waiting for workers to stop .. ")

            # Remove all workers
            self.server_launcher.flush_workers()
            time.sleep(2)

        self.print_graph(perfs, output_folder)

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

        plt.legend(('Accuracy','True Positive Rate','True Negative Rate','False Negative rate','False Positive rate','F1'), loc='upper right')
        plt.xlabel("Threshold values [0-1]")
        plt.ylabel("Indicator value [0-1]")
        plt.title("Performance measure depending on threshold for cluster creation")

        # plt.show()
        plt.savefig(output_path / "overview.png")
        plt.clf()
        plt.cla()
        plt.close()


if __name__ == '__main__':
    param_explorer = ParameterExplorer()

    try:
        # Setting SIGINT handler
        # original_sigint = signal.getsignal(signal.SIGINT)  # Storing original
        param_explorer.launch()

    except KeyboardInterrupt:
        print('Interruption detected')
        try:
            print('Handling interruptions ...')
            param_explorer.server_launcher.stop()
            # param_explorer.client_launcher.stop()
            # TODO : Handle interrupt and shutdown, and clean ...
            sys.exit(0)
        except SystemExit:
            traceback.print_exc(file=sys.stdout)
