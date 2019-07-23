#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pathlib
from pprint import pformat
from typing import List

import carlhauser_client.EvaluationTools.SimilarityGraphExtractor.similarity_graph_quality_evaluator as  graph_quality_evaluator
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import common.Calibrator.calibrator_conf as calibrator_conf
import common.ChartMaker.two_dimensions_plot as two_dimensions_plot
import common.Graph.graph_datastructure as graph_datastructure
import common.ImportExport.json_import_export as json_import_export
import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_server.Configuration import feature_extractor_conf
from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.environment_variable import load_server_logging_conf_file
# from carlhauser_server.Configuration.distance_engine_conf import Default_distance_engine_conf
from carlhauser_server.Configuration.feature_extractor_conf import Default_feature_extractor_conf
from carlhauser_server.Configuration.database_conf import Default_database_conf
from common.environment_variable import dir_path
import common.Scalability_evaluator.scalability_conf as scalability_conf


load_server_logging_conf_file()


class ComputationTime:
    def __init__(self):
        self.feature_time: float = None
        self.adding_time: float = None
        self.request_time: float = None

    def get_sum(self):
        return self.feature_time if not None else 0 + self.adding_time if not None else 0 + self.request_time if not None else 0


class ReponseTime:
    def __init__(self):
        self.response_time: float = None
        self.nb_picture_in_db: int = None
        self.nb_picture_requested: int = None

        # Request time of each
        self.list_request_time: List[ComputationTime] = None


class ScalabilityEvaluator:

    def __init__(self):
        self.logger = logging.getLogger()
        self.ext_api: Extended_API = Extended_API.get_api()

        self.test_db_handler: test_database_handler.TestInstanceLauncher = None
        self.scalability_conf: scalability_conf.Default_scalability_conf = None

    def evaluate_scalability(self,
                             pictures_folder : pathlib.Path,
                             output_folder : pathlib.Path):

        # ==== Separate the folder files ====

        # Extract X pictures to evaluate their matching (at each cycle, the sames)

        # Extract TOTAL - X pictures to upload

        # Put TOTAL-X pictures into boxes (10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000 ...)
        #TODO : Generate them ? Extrapolate ?

        # ==== Upload pictures + Make requests ====

        # For each box

            # Upload pictures of one bin

            # Make request of the X standard pictures

            # Store the request times



# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch DouglasQuaid Scalability Evaluator on your own dataset to get custom scalability measure')
    parser.add_argument("-s", '--source_path', dest="src", required=True, type=dir_path, action='store',
                        help='Source path of folder of pictures to evaluate. Should be a subset of your production data.')
    parser.add_argument("-d", '--dest_path', dest="dest", required=True, type=dir_path, action='store',
                        help='Destination path to store results of the evaluation (configuration files generated, etc.)')

    parser.add_argument("-c", '--conf', dest="conf", type=dir_path, action='store', help='Configuration file (Calibrator_conf) file path.')
    args = parser.parse_args()

    try:
        func = args.func
        calibrator_conf = func(args)
        scalability_evaluator = ScalabilityEvaluator()
        scalability_evaluator.evaluate_scalability(pathlib.Path(args.src),pathlib.Path(args.dest))

    except AttributeError as e:
        parser.error(f"Too few arguments : {e}")
