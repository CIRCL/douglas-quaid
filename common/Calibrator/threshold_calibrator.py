#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pathlib
import time
from typing import List

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import common.Calibrator.calibrator_conf as calibrator_conf
import common.ImportExport.json_import_export as json_import_export
import common.TestInstanceLauncher.test_database_conf as test_database_only_conf
import common.TestInstanceLauncher.test_instance_launcher as test_database_handler
from carlhauser_client.EvaluationTools.GraphExtraction.graph_extractor import GraphExtractor
from carlhauser_server.Configuration import feature_extractor_conf
from carlhauser_server.Configuration.algo_conf import Algo_conf


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
        self.db_conf: test_database_only_conf.TestInstance_database_conf = None
        self.fe_conf: feature_extractor_conf.Default_feature_extractor_conf = None
        self.test_db_handler: test_database_handler.TestInstanceLauncher = None
        self.calibrator_conf: calibrator_conf.Default_calibrator_conf = None

    def set_calibrator_conf(self, calibrator_conf: calibrator_conf.Default_calibrator_conf):
        self.logger.debug("Setting configuration")
        self.calibrator_conf = calibrator_conf
        self.logger.debug("Validation of the configuration ... ")
        calibrator_conf.validate()

    def calibrate_douglas_quaid(self, folder_of_pictures: pathlib.Path,
                                ground_truth_file: pathlib.Path,
                                output_folder: pathlib.Path = None) -> List[Algo_conf]:
        # Outputs a configuration file optimized for the provided dataset and ground truth file
        self.logger.debug("Launching calibration of douglas quaid configuration ... ")

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

        # Call each algorithm evaluator
        calibrated_algos = self.algorithms_evaluator(folder_of_pictures, ground_truth_file, output_folder)

        # save algorithm evaluator results
        json_import_export.save_json(calibrated_algos, output_folder / "calibrated_algo.json")

        return calibrated_algos

    def algorithms_evaluator(self, folder_of_pictures: pathlib.Path,
                             ground_truth_file: pathlib.Path,
                             output_folder: pathlib.Path) -> List[Algo_conf]:
        # Evaluate all algorithms on the specific dataset, returns the "best" configuration file
        # Uses ground truth files and provided pictures list

        self.logger.debug("Iterate over all algorithms ... ")

        default_feature_conf = feature_extractor_conf.Default_feature_extractor_conf()
        list_calibrated_algos = []

        # For each possible algorithm, evaluate the algorithms
        # TODO : Restrict the algorithms list
        for algo in default_feature_conf.list_algos:
            self.logger.debug(f"Current algorithm calibration {algo.algo_name} ... ")

            # Create the output folder for this algo
            tmp_output_folder_algo = (output_folder / algo.algo_name)
            tmp_output_folder_algo.mkdir(exist_ok=True)
            # Evaluation of this algorithm
            calibrated_algo = self.algorithm_evaluator(folder_of_pictures, ground_truth_file, algo, tmp_output_folder_algo)
            # Keeping the best configuration for this algorithm
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
        self.logger.debug(f"Evaluate {to_calibrate_algo.algo_name} ... ")

        # Configurations files
        self.db_conf = test_database_only_conf.TestInstance_database_conf()  # For test sockets only
        self.fe_conf = self.generate_feature_conf(to_calibrate_algo)  # For 1 algo only
        self.de_conf = self.generate_distance_conf()  # For internal inter distance cluster that allow to test all pictures

        # Launch a modified server
        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.db_conf, fe_conf=self.fe_conf)

        time.sleep(5)  # Necessary for the instance to be ready.

        # Launch an evaluator client to extract the graphe
        graph_extractor = GraphExtractor()
        perfs_list, tmp_calibrator_conf = graph_extractor.get_best_algorithm_threshold(image_folder=folder_of_pictures,
                                                                              visjs_json_path=ground_truth_file,
                                                                              output_path=output_folder,
                                                                              calibrator_conf= self.calibrator_conf)

        # Kill server instance
        self.test_db_handler.tearDown()

        # Evaluate the graphe to find thresholds
        # = Already done in thresholds object = thresholds

        # Construct result algo_conf depending on thresholds
        # TOOD : Extract only setted values
        updated_algo_conf = tmp_calibrator_conf.export_to_Algo(to_calibrate_algo)

        return updated_algo_conf  # perfs_list,

    def generate_feature_conf(self, to_calibrate_algo: Algo_conf) -> feature_extractor_conf.Default_feature_extractor_conf:
        # Generate a feature configuration object with only one algorithm activated

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

    def generate_distance_conf(self) -> distance_engine_conf.Default_distance_engine_conf:
        # Generate a distance configuration object which is less performant but with maximal score in quality

        de_conf = distance_engine_conf.Default_distance_engine_conf()
        de_conf.MAX_DIST_FOR_NEW_CLUSTER = 1  # Only one big cluter with a lot of pictures. Will check all pictures.

        return de_conf


def dir_path(path):
    if pathlib.Path(path).exists():
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def default_conf(args):
    cal_conf = calibrator_conf.Default_calibrator_conf.get_default_instance()
    return cal_conf

def load_from_file(args):
    cal_conf = calibrator_conf.Default_calibrator_conf()
    #TODO : Load from file !
    return cal_conf


def load_from_args(args):
    # Create a calibrator configuration from args

    cal_conf = calibrator_conf.Default_calibrator_conf()
    cal_conf.Acceptable_false_positive_rate = args.AFPR
    cal_conf.Acceptable_false_negative_rate = args.AFNR
    cal_conf.Minimum_true_positive_rate = args.MTPR
    cal_conf.Minimum_true_negative_rate = args.MTNR

    # validate the values
    cal_conf.validate()

    return cal_conf


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    # Launch command examples :
    # python3 ./threshold_calibrator.py -s -gt -d from_conf_file
    # python3 ./threshold_calibrator.py -s ./../../datasets/MINI_DATASET -gt ./../../datasets/MINI_DATASET_VISJS.json -d ./TEST/ from_cmd_args -AFPR 0.1 -MTPR 0.9
    parser = argparse.ArgumentParser(description='Launch DouglasQuaid Calibrator on your own dataset to get custom configuration files')
    parser.add_argument("-s", '--source_path', dest="src", required=True, type=dir_path, action='store',
                        help='Source path of folder of pictures to evaluate. Should be a subset of your production data.')
    parser.add_argument("-gt", '--ground_truth', dest="gt", required=True, type=dir_path, action='store',
                        help='Ground truth file path which has clustered version of the provided data. Very important as it is on what the optimization will based its calculations !')
    parser.add_argument("-d", '--dest_path', dest="dest", required=True, type=dir_path, action='store',
                        help='Destination path to store results of the evaluation (configuration files generated, etc.)')

    subparsers = parser.add_subparsers(help='Handle a configuration file')

    # create the parser for the "command_0" command
    parser_a = subparsers.add_parser('from_default', help='Set-up expected values/thresholds from default configuration')
    parser_a.set_defaults(func=default_conf)

    # create the parser for the "command_1" command
    parser_a = subparsers.add_parser('from_conf_file', help='Set-up expected values/thresholds from configuration file')
    parser_a.add_argument("-c", '--conf', dest="conf", type=dir_path, action='store', help='Configuration file (Calibrator_conf) file path.')
    parser_a.set_defaults(func=load_from_file)

    # create the parser for the "command_2" command
    parser_b = subparsers.add_parser('from_cmd_args', help='Set-up expected values/thresholds from command line [(TNR or FPR) AND (TPR or FNR)]')
    parser_b.add_argument('-AFPR', dest="AFPR", type=float, action='store', help='Acceptable False Positive Rate (target)')
    parser_b.add_argument('-AFNR', dest="AFNR", type=float, action='store', help='Acceptable False Positive Rate (target)')
    parser_b.add_argument('-MTPR', dest="MTPR", type=float, action='store', help='Minimum True Positive Rate (target)')
    parser_b.add_argument('-MTNR', dest="MTNR", type=float, action='store', help='Minimum True Negative Rate (target)')
    parser_b.set_defaults(func=load_from_args)

    args = parser.parse_args()

    try:
        func = args.func
        calibrator_conf = func(args)
        calibrator = Calibrator()
        calibrator.set_calibrator_conf(calibrator_conf)
        calibrator.calibrate_douglas_quaid(folder_of_pictures=pathlib.Path(args.src),
                                           ground_truth_file=pathlib.Path(args.gt),
                                           output_folder=pathlib.Path(args.dest))

    except AttributeError as e:
        parser.error(f"Too few arguments : {e}")
