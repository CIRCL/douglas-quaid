#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pathlib
import pprint
from typing import List
import time

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Singletons.database_start_stop as database_start_stop
import carlhauser_server.instance_handler as core
import common.Graph.graph_datastructure as graph_datastructure
import common.ImportExport.json_import_export as json_import_export
import common.TestInstanceLauncher.test_instance_launcher as test_database_handler
from carlhauser_server.Configuration import feature_extractor_conf as feature_extractor_conf
from common.ImportExport.json_import_export import Custom_JSON_Encoder
from common.environment_variable import get_homedir
import common.TestInstanceLauncher.test_database_conf as test_database_only_conf
from carlhauser_server.Configuration.algo_conf import Algo_conf
from carlhauser_client.EvaluationTools.GraphExtraction.graph_extractor import GraphExtractor


class Calibrator:
    """ Create an instance of douglas quaid for each algorithm and for each threshold :
        send provided pictures, get quality statistics compared with provided ground truth file
        and do it again. Outputs a fine tuned config file at the end. """

    def __init__(self):
        self.logger = logging.getLogger()

        # Inputs
        '''
        self.folder_of_pictures = None
        self.ground_truth_file = None
        self.output_folder = None
        '''
        self.db_conf : test_database_only_conf.TestInstance_database_conf = None
        self.fe_conf : feature_extractor_conf.Default_feature_extractor_conf = None
        self.test_db_handler : test_database_handler.TestInstanceLauncher = None

    def calibrate_douglas_quaid(self, folder_of_pictures: pathlib.Path,
                                ground_truth_file: pathlib.Path,
                                output_folder: pathlib.Path = None) -> List[Algo_conf]:

        # Check inputs
        if not folder_of_pictures.exists():
            raise Exception(f"Folder of picture {folder_of_pictures} does not exist ! Please check path. ")
        if not ground_truth_file.exists():
            raise Exception(f"Ground truth file {ground_truth_file} does not exist ! Please check path. ")

        # Verify output folder
        if not output_folder.exists():
            try:
                output_folder.mkdir()
            except:
                raise Exception(f"Output folder does not exist and impossible to create it. Aborting. Please check permissions (most likely)")

        self.logger.debug("Paths provided checked and corrects.")

        # Load ground truth file / Verify ground truth file
        visjs = json_import_export.load_json(ground_truth_file)
        graph = graph_datastructure.GraphDataStruct.load_from_dict(visjs)
        self.logger.debug("Ground truth file loaded as graph.")

        # Load pictures / verify pictures
        p = folder_of_pictures.resolve().glob('**/*')
        files = [x for x in p if x.is_file()]
        files.sort()
        self.logger.debug(f"{len(files)} files readable in {folder_of_pictures} and below")

        # Call each algorithm evaluator
        calibrated_algos = self.algorithms_evaluator(folder_of_pictures, ground_truth_file, output_folder)

        # save algorithm evaluator results
        json_import_export.save_json(calibrated_algos, output_folder / "calibrated_algo.json")

        return calibrated_algos

    def algorithms_evaluator(self, folder_of_pictures: pathlib.Path,
                             ground_truth_file: pathlib.Path,
                             output_folder: pathlib.Path) -> List[Algo_conf]:
        # Evaluate one algorithm
        # Uses ground truth files and provided pictures list

        default_feature_conf = feature_extractor_conf.Default_feature_extractor_conf()
        list_calibrated_algos = []

        for algo in default_feature_conf.list_algos:
            tmp_output_folder_algo = (output_folder / algo.algo_name)
            tmp_output_folder_algo.mkdir(exist_ok=True)
            calibrated_algo = self.algorithm_evaluator(folder_of_pictures, ground_truth_file, algo, tmp_output_folder_algo)
            list_calibrated_algos.append(calibrated_algo)

        return list_calibrated_algos

    '''
        # HASH parameters
        self.A_HASH = Algo_conf("A_HASH", False, 0.2, 0.6, distance_weight=1)
        self.P_HASH = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        self.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.6, distance_weight=1)
        self.D_HASH = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        self.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, 0.2, 0.6, distance_weight=1)
        self.W_HASH = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        self.TLSH = Algo_conf("TLSH", True, 0.2, 0.6, distance_weight=1)

        # Visual Descriptors parameters
        self.ORB = Algo_conf("ORB", True, 0.2, 0.6, distance_weight=5)
        self.ORB_KEYPOINTS_NB = 500
    '''

    def algorithm_evaluator(self, folder_of_pictures: pathlib.Path,
                            ground_truth_file: pathlib.Path,
                            to_calibrate_algo: Algo_conf,
                            output_folder: pathlib.Path = None) -> Algo_conf:
        # Take an algorithm to calibrate and return a calibrated version of this algo (of its threshold, exactly)
        # Uses the ground truth files and provided pictures list

        # Configurations files
        self.db_conf = test_database_only_conf.TestInstance_database_conf()
        self.fe_conf = self.generate_feature_conf(to_calibrate_algo)


        '''
        self.dist_conf = None
        self.fe_conf = # TODO : Construct feature extractor configuration
        self.ws_conf = None
        self.core_launcher = None
        '''

        # TODO : Choose threshold for server == Modify db conf/feature conf / ...

        # Launch a modified server
        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.db_conf, fe_conf=self.fe_conf)

        time.sleep(5)
        # Launch an evaluator client to extract the graphe
        # TODO : Create client : myclient = AlgoEvaluatorClient
        graph_extractor = GraphExtractor()
        perfs_list = graph_extractor.launch(image_folder=folder_of_pictures,
                               visjs_json_path=ground_truth_file,
                               output_path=output_folder)

        # Kill server instance
        self.test_db_handler.tearDown()

        # Evaluate the graphe to find thresholds
        # TODO : work with perfs_list

        # Construct result algo_conf depending on thresholds
        # TODO : work with perfs_list

        return perfs_list

    def generate_feature_conf(self, to_calibrate_algo: Algo_conf) -> feature_extractor_conf.Default_feature_extractor_conf:
        fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        DEFAULT_LOW = 0
        DEFAULT_HIGH = 1
        fe_conf.A_HASH = Algo_conf("A_HASH", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)
        fe_conf.P_HASH = Algo_conf("P_HASH", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)
        fe_conf.P_HASH_SIMPLE = Algo_conf("P_HASH_SIMPLE", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)
        fe_conf.D_HASH = Algo_conf("D_HASH", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)
        fe_conf.D_HASH_VERTICAL = Algo_conf("D_HASH_VERTICAL", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)
        fe_conf.W_HASH = Algo_conf("W_HASH", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)
        fe_conf.TLSH = Algo_conf("TLSH", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)
        fe_conf.ORB = Algo_conf("ORB", False, DEFAULT_LOW, DEFAULT_HIGH, distance_weight=1)

        # Reset current algorithm object values
        to_calibrate_algo.distance_weight = 1
        to_calibrate_algo.decision_weight = 1
        to_calibrate_algo.is_enabled = True

        # Put the algorithm to activate
        if to_calibrate_algo.algo_name == "A_HASH":
            fe_conf.A_HASH = to_calibrate_algo
        elif to_calibrate_algo.algo_name == "P_HASH":
            fe_conf.P_HASH = to_calibrate_algo
        elif to_calibrate_algo.algo_name == "P_HASH_SIMPLE":
            fe_conf.P_HASH_SIMPLE = to_calibrate_algo
        elif to_calibrate_algo.algo_name == "D_HASH":
            fe_conf.D_HASH = to_calibrate_algo
        elif to_calibrate_algo.algo_name == "D_HASH_VERTICAL":
            fe_conf.D_HASH_VERTICAL = to_calibrate_algo
        elif to_calibrate_algo.algo_name == "W_HASH":
            fe_conf.W_HASH = to_calibrate_algo
        elif to_calibrate_algo.algo_name == "TLSH":
            fe_conf.TLSH = to_calibrate_algo
        elif to_calibrate_algo.algo_name == "ORB":
            fe_conf.ORB = to_calibrate_algo
        else:
            raise Exception("Unhandled algo name. Structural problem in threshold_calibrator")

        fe_conf.list_algos = [fe_conf.A_HASH, fe_conf.P_HASH, fe_conf.P_HASH_SIMPLE,
                              fe_conf.D_HASH, fe_conf.D_HASH_VERTICAL, fe_conf.W_HASH,
                              fe_conf.TLSH,
                              fe_conf.ORB]

        # Reset distance and decision merging method
        fe_conf.DISTANCE_MERGING_METHOD = feature_extractor_conf.Distance_MergingMethod.MAX.name
        fe_conf.DECISION_MERGING_METHOD = feature_extractor_conf.Decision_MergingMethod.MAJORITY.name

        return fe_conf
