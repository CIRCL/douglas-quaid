#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import sys
import time
import traceback

import carlhauser_client.EvaluationTools.StorageGraphExtractor.storage_quality_evaluator as evaluator
import carlhauser_server.instance_handler as instance_handler
import common.ChartMaker.two_dimensions_plot as two_dimensions_plot
import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
from common.environment_variable import get_homedir
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


# ==================== ------ LAUNCHER ------- ====================
class ParameterExplorer:
    '''
    Extract parameters and quality of the storage graph. TODO : Should be reviewed and modified.
    '''

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

        iterations_limit = 50  # Or nb of iteration if complete exploration

        max_threshold = 1
        min_threshold = 0

        # ========= CONFIGURATION CHOSING =========

        for i in range(iterations_limit):

            # Computing the new threshold
            curr_threshold = i * ((max_threshold - min_threshold) / iterations_limit)
            self.logger.info(f"Current threshold computation : {curr_threshold}")

            # If the instance already exist, delete it
            if self.server_launcher is not None:
                del self.server_launcher

            # Put configuration in place
            self.server_launcher = instance_handler.Instance_Handler()
            self.server_launcher.dist_conf.MAX_DIST_FOR_NEW_CLUSTER = curr_threshold

            # Create output folder for this configuration
            tmp_output = output_folder / ''.join([str(curr_threshold), "_threshold"])
            tmp_output.mkdir(parents=True, exist_ok=True)

            # ========= CONFIGURATION LAUNCH =========

            # Launch Server
            self.server_launcher.launch()
            time.sleep(2)

            # Launch client tester
            self.client_launcher = evaluator.InternalClusteringQualityEvaluator()
            perf_overview = self.client_launcher.get_storage_graph(image_folder, gt, tmp_output)
            self.logger.warning(f"Perf overview added : {perf_overview}")

            perfs.append(perf_datastruct.Perf(perf_overview, curr_threshold))

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

        # Print plot
        TwoD_plot = two_dimensions_plot.TwoDimensionsPlot()
        TwoD_plot.print_graph(perfs, output_folder)


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
