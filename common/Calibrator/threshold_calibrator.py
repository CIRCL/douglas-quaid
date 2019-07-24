#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pathlib
from pprint import pformat
from typing import List
import time

import carlhauser_client.EvaluationTools.SimilarityGraphExtractor.similarity_graph_quality_evaluator as  graph_quality_evaluator
import carlhauser_client.EvaluationTools.SimilarityGraphExtractor.similarity_graph_extractor as  similarity_graph_extractor
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
from common.environment_variable import dir_path, make_big_line

load_server_logging_conf_file()


class Calibrator:
    """ Create an instance of douglas quaid for each algorithm and for each threshold :
        send provided pictures, get quality statistics compared with provided ground truth file
        and do it again. Outputs a fine tuned config file at the end. """

    def __init__(self):
        self.logger = logging.getLogger()
        self.ext_api: Extended_API = Extended_API.get_api()

        # Inputs
        '''
        self.folder_of_pictures = None
        self.ground_truth_file = None
        self.output_folder = None
        '''
        # self.db_conf: test_database_only_conf.TestInstance_database_conf = None
        # self.fe_conf: feature_extractor_conf.Default_feature_extractor_conf = None
        # self.de_conf: distance_engine_conf.Default_distance_engine_conf = None
        self.test_db_handler: test_database_handler.TestInstanceLauncher = None
        self.cal_conf: calibrator_conf.Default_calibrator_conf = None

    def set_calibrator_conf(self, tmp_calibrator_conf: calibrator_conf.Default_calibrator_conf):
        self.logger.debug("Setting configuration")
        self.cal_conf = tmp_calibrator_conf
        self.logger.debug("Validation of the configuration ... ")
        tmp_calibrator_conf.validate()

    def calibrate_douglas_quaid(self, folder_of_pictures: pathlib.Path,
                                ground_truth_file: pathlib.Path,
                                output_folder: pathlib.Path = None) -> List[Algo_conf]:
        """
        Outputs a configuration file optimized for the provided dataset and ground truth file,
        given expected threshold TP/FP goals specified in calibrator configuration
        :param folder_of_pictures: The folder of pictures on which to calibrate (subset of a bigger dataset)
        :param ground_truth_file: The path to the ground truth file used as the "perfect matches", as a goal to reach
        :param output_folder: Path to folder where results will be saved
        :return: A list of AlgoConfiguraiton (including thresholds for YES/MAYBE/NO from their distance outputs)
        """
        self.logger.debug("Launching calibration of douglas quaid configuration ... ")
        start_time = time.time()

        # Verify if path are corrects
        self.check_inputs(folder_of_pictures, ground_truth_file, output_folder)

        # Call each algorithm evaluator
        calibrated_algos = self.calibrate_each_algo_separately(folder_of_pictures, ground_truth_file, output_folder)

        # Save algorithm evaluator results
        json_import_export.save_json(calibrated_algos, output_folder / "calibrated_algo.json")

        # Translate list of algorithms to correct configuration file for carl-hauser
        configuration_file = feature_extractor_conf.calibrated_algos_to_conf_file(calibrated_algos)

        # Save algorithm evaluator results
        json_import_export.save_json(configuration_file, output_folder / "calibrated_fe_conf.json")

        # Call evaluator on all algorithms at once, to get the threshold to constitute clusters
        calibrated_algo_set = self.calibrate_std_algo_set(folder_of_pictures, ground_truth_file, output_folder)

        # Save algorithm evaluator results
        json_import_export.save_json(calibrated_algos, output_folder / "calibrated_algo_set.json")

        # Construct result algo_conf depending on thresholds
        self.logger.debug(f"Export to algorithm configuration")
        dist_conf_calibrated = calibrator_conf.calibrator_conf_to_conf_file(calibrated_algo_set)

        # Save algorithm evaluator results
        json_import_export.save_json(dist_conf_calibrated, output_folder / "dist_conf_calibrated.json")

        make_big_line()
        self.logger.info(f"Calibration completed in {abs(start_time-time.time())}s")

        return calibrated_algos

    def check_inputs(self, folder_of_pictures: pathlib.Path,
                     ground_truth_file: pathlib.Path,
                     output_folder: pathlib.Path = None):
        """
        Verify if input paths are valid. Throw exception if not.
        :param folder_of_pictures: The folder of pictures on which to calibrate (subset of a bigger dataset)
        :param ground_truth_file: The path to the ground truth file used as the "perfect matches", as a goal to reach
        :param output_folder: Path to folder where results will be saved
        :return: Nothing, Exception if error.
        """

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
        self.logger.debug("Verification of ground truth graph and files folder")

        gt_graph = graph_datastructure.load_visjs_to_graph(ground_truth_file)

        file_list = set()
        for image_path in folder_of_pictures.iterdir():
            if image_path.is_file():
                file_list.add(image_path.name)

        images_set, labels_set = gt_graph.get_nodes_not_included(file_list)

        if len(images_set) == 0 or len(labels_set) == 0 :
            self.logger.debug("Files names are included in the graph. Continuing ... ")
        else :
            self.logger.error("Files names are not included in the graph. If continuing, the calibrator will encounter error during evaluation phase. Cancelling ...")
            raise Exception("File names not in ground truth file. Please review ground truth file or input images folder")

    def calibrate_each_algo_separately(self, folder_of_pictures: pathlib.Path,
                                       ground_truth_file: pathlib.Path,
                                       output_folder: pathlib.Path) -> List[Algo_conf]:
        """
        Evaluate each possible algorithm on the specific dataset, returns the "best" configuration file for each
        Uses ground truth files and provided pictures list to optimize goals setted in calibrator conf
        :param folder_of_pictures: The folder of pictures on which to calibrate (subset of a bigger dataset)
        :param ground_truth_file: The path to the ground truth file used as the "perfect matches", as a goal to reach
        :param output_folder: Path to folder where results will be saved
        :return: List of Algorithms configuration modified with "good" thresholds
        """

        self.logger.debug("Iterate over all algorithms ... ")

        default_feature_conf = feature_extractor_conf.Default_feature_extractor_conf()
        list_calibrated_algos = []

        # For each possible algorithm, evaluate the algorithms
        # TODO : Restrict the algorithms list
        for to_calibrate_algo in default_feature_conf.list_algos:
            self.logger.debug(f"Current algorithm calibration {to_calibrate_algo.algo_name} ... ")

            # Create the output folder for this algo
            tmp_output_folder_algo = (output_folder / to_calibrate_algo.algo_name)
            tmp_output_folder_algo.mkdir(exist_ok=True)

            # Configurations files
            db_conf = test_database_only_conf.TestInstance_database_conf()  # For test sockets only
            fe_conf = self.generate_feature_conf(to_calibrate_algo)  # For 1 algo only
            # de_conf = self.generate_distance_conf()  # For internal inter distance cluster that allow to test all pictures

            # Evaluation of this algorithm
            _, tmp_calibrator_conf = self.create_instance_and_calibrate(db_conf, fe_conf, folder_of_pictures, ground_truth_file, tmp_output_folder_algo)

            # Construct result algo_conf depending on thresholds
            self.logger.debug(f"Export to algorithm configuration")
            calibrated_algo = tmp_calibrator_conf.export_to_Algo(to_calibrate_algo)

            self.logger.debug(f"Calibrated algorithm {to_calibrate_algo.algo_name} with : {calibrated_algo} ")

            # Keeping the best configuration for this algorithm
            list_calibrated_algos.append(calibrated_algo)

        return list_calibrated_algos

    def calibrate_std_algo_set(self, folder_of_pictures: pathlib.Path,
                               ground_truth_file: pathlib.Path,
                               output_folder: pathlib.Path = None) -> calibrator_conf.Default_calibrator_conf:
        """
        Returns a distance configuration file calibrated to optimize given metrics on ground truth files and provided pictures list.
        :param folder_of_pictures: The folder of pictures on which to calibrate (subset of a bigger dataset)
        :param ground_truth_file: The path to the ground truth file used as the "perfect matches", as a goal to reach
        :param output_folder: Path to folder where results will be saved
        :return: The distance configuration file calibrated (with good cluster threshold)
        """

        self.logger.debug(f"Evaluate standard configuration ... ")

        # Configurations files
        db_conf = test_database_only_conf.TestInstance_database_conf()  # For test sockets only
        fe_conf = feature_extractor_conf.Default_feature_extractor_conf()  # For current standard configuration
        # de_conf = self.generate_distance_conf()  # For internal inter distance cluster that allow to test all pictures
        tmp_output_folder_algo = (output_folder / "STD_ALGO_SET")

        _, tmp_calibrator_conf = self.create_instance_and_calibrate(db_conf, fe_conf, folder_of_pictures, ground_truth_file, tmp_output_folder_algo)

        return tmp_calibrator_conf

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

    def create_instance_and_calibrate(self,
                                      db_conf: Default_database_conf,
                                      fe_conf: Default_feature_extractor_conf,
                                      # Unused ? # de_conf : Default_distance_engine_conf,
                                      folder_of_pictures: pathlib.Path,
                                      ground_truth_file: pathlib.Path,
                                      output_folder: pathlib.Path = None) -> (List[perf_datastruct.Perf], calibrator_conf.Default_calibrator_conf):
        """
        Create an instance of a server and client only working on a temporary database (test db).
        Calibrate distance threshold given provided configuration file (an so which algorithms to activate together) and
        ground truth files and provided pictures list. Modify calibrator configuration and returns a list of performance object as results.
        :param db_conf: The database configuration file (should be "in test only" mode)
        :param fe_conf: The feature extractor configuration file (Can be default one, or custom one, with only algorithms to evaluate together)
        :param folder_of_pictures: The folder of pictures on which to calibrate (subset of a bigger dataset)
        :param ground_truth_file: The path to the ground truth file used as the "perfect matches", as a goal to reach
        :param output_folder: Path to folder where results will be saved
        :return: List of performance object (each possible value of the threshold) and a modified calibrator configuration
        """

        # Launch a modified server
        self.logger.debug(f"Creation of a full instance of redis (Test only) ... ")
        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=db_conf, fe_conf=fe_conf)

        # Launch an evaluator client to extract the graphe
        self.logger.debug(f"Launching Algorithm evaluation ... ")
        perfs_list, tmp_calibrator_conf = self.get_best_thresholds(image_folder=folder_of_pictures,
                                                                   visjs_json_path=ground_truth_file,
                                                                   output_path=output_folder,
                                                                   cal_conf=self.cal_conf)

        # Kill server instance
        self.logger.debug(f"Shutting down Redis test instance")
        self.test_db_handler.tearDown()

        # input()

        return perfs_list, tmp_calibrator_conf

    '''

    def algorithm_evaluator(self, folder_of_pictures: pathlib.Path,
                            ground_truth_file: pathlib.Path,
                            to_calibrate_algo: Algo_conf,
                            output_folder: pathlib.Path = None) -> Algo_conf:
        """
        Given as input an algorithm to calibrate, returns a calibrated version of this same algo (changes its threshold, exactly)
        Uses the ground truth files and provided pictures list
        :param folder_of_pictures: The folder of pictures on which to calibrate (subset of a bigger dataset)
        :param ground_truth_file: The path to the ground truth file used as the "perfect matches", as a goal to reach
        :param to_calibrate_algo: Algorithm to find thresholds
        :param output_folder: Path to folder where results will be saved
        :return: Same algo configuration, modified with computed "good" thresholds
        """
        #
        #
        self.logger.debug(f"Evaluate {to_calibrate_algo.algo_name} ... ")

        # Configurations files
        self.db_conf = test_database_only_conf.TestInstance_database_conf()  # For test sockets only
        self.fe_conf = self.generate_feature_conf(to_calibrate_algo)  # For 1 algo only
        self.de_conf = self.generate_distance_conf()  # For internal inter distance cluster that allow to test all pictures

        # Launch a modified server
        self.logger.debug(f"Creation of a full instance of redis (Test only) ... ")
        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.db_conf, fe_conf=self.fe_conf)

        # Launch an evaluator client to extract the graphe
        self.logger.debug(f"Launching Algorithm evaluation ... ")
        perfs_list, tmp_calibrator_conf = self.get_best_thresholds(image_folder=folder_of_pictures,
                                                                   visjs_json_path=ground_truth_file,
                                                                   output_path=output_folder,
                                                                   cal_conf=self.calibrator_conf)

        # Kill server instance
        self.logger.debug(f"Shutting down Redis test instance")
        self.test_db_handler.tearDown()

        # Construct result algo_conf depending on thresholds
        self.logger.debug(f"Export to algorithm configuration")
        updated_algo_conf = tmp_calibrator_conf.export_to_Algo(to_calibrate_algo)

        return updated_algo_conf  # perfs_list,
    '''

    @staticmethod
    def generate_feature_conf(to_calibrate_algo: Algo_conf) -> feature_extractor_conf.Default_feature_extractor_conf:
        """
        Generate a feature configuration object with only one algorithm activated
        :param to_calibrate_algo: Algo configuration evaluate
        :return: Modified Feature configuration
        """

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

    @staticmethod
    def generate_distance_conf() -> distance_engine_conf.Default_distance_engine_conf:
        """
        Generate a distance configuration object which is less performant but with maximal score in quality
        :return: Modified Distance Engine Configuration
        """

        de_conf = distance_engine_conf.Default_distance_engine_conf()
        de_conf.MAX_DIST_FOR_NEW_CLUSTER = 1  # Only one big cluter with a lot of pictures. Will check all pictures.

        return de_conf

    def get_best_thresholds(self, image_folder: pathlib.Path,
                            output_path: pathlib.Path,
                            visjs_json_path: pathlib.Path,
                            cal_conf: calibrator_conf.Default_calibrator_conf) -> (List[perf_datastruct.Perf], calibrator_conf.Default_calibrator_conf):
        '''
        Compute the best threshold to apply to distance to have an optimized number of False Positive, True Positive, etc.
        :param image_folder: The folder of picture to send and request, to optimize parameters for
        :param output_path: The output path where the graph and other data will be stored
        :param visjs_json_path: The "ground truth" file that serves as reference to optimize False Positive, etc.
        :param cal_conf: Values of False Positive, True Positive, etc. expected
        :return: List of performance values (threshold + False Positive, True Positive, etc. performances) and a modified cal_conf with "best threshold" regarding False Positive, True Positive, etc. target values
        '''

        # Get results from DB and ground truth graph from visjs file
        self.logger.debug(f"Sending pictures ... ")
        list_results = self.ext_api.add_and_request_and_dump_pictures(image_folder)

        # Save to file
        json_import_export.save_json(list_results, output_path / "requests_result.json")
        self.logger.debug(f"Results raw json saved.")

        '''
        # Load ground truth file
        gt_graph = graph_datastructure.load_visjs_to_graph(visjs_json_path)

        # Call the graph evaluator on this pair result_list + gt_graph
        self.logger.debug(f"Extracting performance list ")
        perf_eval = graph_quality_evaluator.similarity_graph_quality_evaluator(cal_conf)
        perfs_list = perf_eval.get_perf_list(list_results, gt_graph)  # ==> List of scores
        self.logger.debug(f"Fetched performance list : {pformat(perfs_list)} ")
        '''
        # Load ground truth file and evaluate
        graph_extractor = similarity_graph_extractor.GraphExtractor()
        perfs_list = graph_extractor.evaluate_list_results(list_results, visjs_json_path, output_path, cal_conf)

        # Save to file
        json_import_export.save_json(perfs_list, output_path / "graph_perfs.json")
        self.logger.debug(f"Graph performances json saved.")

        # Save to graph
        twoDplot = two_dimensions_plot.TwoDimensionsPlot()
        twoDplot.print_graph(perfs_list, output_path)

        # TODO : copy_cal_conf = cal_conf.deepcopy()
        copy_cal_conf = cal_conf

        self.logger.debug(f"Current configuration : {copy_cal_conf} ")

        # Call the graph evaluator on result_list + gt_graph
        if copy_cal_conf.Minimum_true_positive_rate is not None:
            thre_max_TPR, val_TPR = self.get_threshold_where_upper_are_more_than_xpercent_TP(perfs_list=perfs_list,
                                                                                             percent=copy_cal_conf.Minimum_true_positive_rate)
            copy_cal_conf.thre_upper_at_least_xpercent_TPR = thre_max_TPR

        if copy_cal_conf.Acceptable_false_negative_rate is not None:
            thre_max_FNR, val_FNR = self.get_threshold_where_upper_are_less_than_xpercent_FN(perfs_list=perfs_list,
                                                                                             percent=copy_cal_conf.Acceptable_false_negative_rate)
            copy_cal_conf.thre_upper_at_most_xpercent_FNR = thre_max_FNR

        if copy_cal_conf.Minimum_true_negative_rate is not None:
            thre_max_TNR, val_TNR = self.get_threshold_where_below_are_more_than_xpercent_TN(perfs_list=perfs_list,
                                                                                             percent=copy_cal_conf.Minimum_true_negative_rate)
            copy_cal_conf.thre_below_at_least_xpercent_TNR = thre_max_TNR

        if copy_cal_conf.Acceptable_false_positive_rate is not None:
            thre_max_FPR, val_FPR = self.get_threshold_where_below_are_less_than_xpercent_FP(perfs_list=perfs_list,
                                                                                             percent=copy_cal_conf.Acceptable_false_positive_rate)
            copy_cal_conf.thre_below_at_most_xpercent_FPR = thre_max_FPR

        thre_max_F1, val_F1 = self.get_max_threshold_for_max_F1(perfs_list=perfs_list)
        copy_cal_conf.maximum_F1 = thre_max_F1

        self.logger.debug(f"Computed thresholds {copy_cal_conf} ")

        # Save to graph
        twoDplot.print_graph_with_thresholds(perfs_list, copy_cal_conf, output_path)

        return perfs_list, copy_cal_conf

    '''
            +--------------------------+
            |X       way of iteration  |
            |  X       +------->       |
            | ^  X                     |
            | |    X                   |
            | |    ^ X                 |
            | |    |   X               |
            | |    |     X             |
            | |    |       X           |
            | |    |         X         |
            | |    |          ^X       |
            | |    |          |  X     |
            | |    |          |    X   |
            | |    |          |    ^ X |
            +-+----+----------+----+---+
       leftmost  righmost    leftmost  rightmost
       higher    higher      lower     lower
          1        2           3         4

          1 = leftmost higher (decreasing) = righmost higher (increasing)
          2 = righmost higher (decreasing) = righmost lower (increasing)
          3 = leftmost lower (decreasing) = leftmost higher (increasing)
          4 = rightmost lower (decreasing) = leftmost lower (increasing)

               +--------------------------+
               |        way of iterationX |
               |          +------->   X   |
               |                    X   ^ |
               |                  X     | |
               |                X  ^    | |
               |              X    |    | |
               |            X      |    | |
               |          X        |    | |
               |        X          |    | |
               |      X            |    | |
               |    X ^            |    | |
               |  X   |            |    | |
               |X^    |            |    | |
               +--------------------------+
          leftmost  leftmost    righmost  rightmost
          lower     higher      lower     higher
              4        3           2         1
              
        We always fallback on first case
       
    '''

    def get_optimal_for_optimized_attribute(self, perfs_list: List[perf_datastruct.Perf],
                                            attribute: str,
                                            rightmost: bool = True,
                                            higher=False,
                                            is_increasing: bool = True,
                                            tolerance: float = 0.1):
        """
        Extract the threshold for a specific kind of value
        rightmost, higher = Get the rightmost higher value of the attribute
        rightmost, lower = Get the rightmost lower value of the attribute, with attribute > Tolerance of the graph_evaluator
        leftmost, higher = Get the leftmost higher value of the attribute, with attribute < Tolerance of the graph_evaluator
        leftmost, lower = Get the leftmost lower value of the attribute
        :param perfs_list: List of object (Perf object)
        :param attribute: Which attribute of the object in the object list to look for : TP,TN,FP,FN, ...
        :param rightmost: Boolean, True = We are looking for the rightmost value. False = We are looking for the leftmost value (absciss)
        :param higher: Boolean, True = We are looking for the highest value. False = We are looking for the lower value (ordinate axis)
        :param is_increasing: is_increasing define if the graph is going up and up or not.
        :param tolerance:
        :return:
        """

        if len(perfs_list) == 0:
            raise Exception("Performance list empty ! Impossible to get threshold out of it.")

        # We could have assumed the performance list is sorted
        '''
        l = [1,2,5,3,7]
        l.sort() = [1, 2, 3, 5, 7]
        '''
        perfs_list.sort(key=lambda k: k.threshold, reverse=is_increasing)

        # Explanation in the previous graphs above the function header
        if is_increasing:
            if rightmost and higher:
                rightmost = not rightmost
            elif rightmost and not higher:
                higher = not higher
            elif not rightmost and higher:
                higher = not higher
            elif not rightmost and not higher:
                rightmost = not rightmost

        # We want a decreasing graph, always.
        self.logger.debug(f"Threshold list : {[round(p.threshold, 2) for p in perfs_list]}")
        self.logger.debug(f"Perf list :      {[round(getattr(p.score, attribute), 2) for p in perfs_list]}")

        if rightmost is False and higher:
            self.logger.debug(f"On the equivalent decreasing graph, we want [1] the leftmost higher value of the attribute {attribute}")
            return self.get_max_threshold_for_max_attr(perfs_list, attribute)

        elif rightmost and higher:
            self.logger.debug(f"On the equivalent decreasing graph, We want [2] the rightmost higher value of the attribute {attribute} with attribute > {tolerance}")
            return self.get_min_threshold_for_max_attr_with_tolerance(perfs_list, attribute, tolerance)

        elif rightmost is False and higher is False:
            self.logger.debug(f"On the equivalent decreasing graph, We want [3] the leftmost lower value of the attribute {attribute} with attribute > {tolerance}")
            return self.get_min_threshold_for_max_attr_with_tolerance(perfs_list, attribute, tolerance)

        elif rightmost and higher is False:
            self.logger.debug(f"On the equivalent decreasing graph, We want [4] the rightmost lower value of the attribute {attribute} ")
            return self.get_min_threshold_for_min_attr(perfs_list, attribute)

        '''
             +--------------------------+
             |X       way of iteration  |
             |  X       +------->       |
             |    X                     |
             |      X                   |
             |        X                 |
             |          X               |
             |            X             |
             |              X           |
    returned |                X         |
    value    +---------+--------X-------+
             |         ^         ^X     |
             |tolerance|         |  X   |
             |         |         |    X |
             +---------+---------+------+
             0                  0.9     1
                    Returned threshold
        '''

    @staticmethod
    def get_min_threshold_for_max_attr_with_tolerance(perfs_list: List[perf_datastruct.Perf],
                                                      attribute: str,
                                                      tolerance: float) -> (float, float):
        """
        Work on a decreasing graph ONLY !
        Dummy constraint search. At the point where the constraint (be above the threshold)
        is broken, we break and return the found values.
        :param perfs_list: List of object (Perf object)
        :param attribute: Which attribute of the object in the object list to look for : TP,TN,FP,FN, ...
        :param tolerance: threshold, on ordinates. The graph has to be lower than this value at some point.
        :return: The threshold and the value of the max of the graph, within the "tolerance" band
        """

        # Note : we could have a much simpler version,
        # where we filter out all perfObject with value above "tolerance".
        # Then we fetch the first (leftmost) perf of the list, and return its threshold/value

        threshold, max_value = Calibrator._get_initial_values(perfs_list, attribute)

        for curr_perf in perfs_list:
            curr_value = getattr(curr_perf.score, attribute)
            if curr_value >= tolerance:
                threshold = curr_perf.threshold
            else:
                break

        return threshold, max_value

    '''
          +--------------------------+
 returned |X       way of iteration  |
 value    |  X       +------->       |
          | ^  X                     |
          | |    X                   |
          | |      X                 |
          | |        X               |
          | |          X             |
          | |            X           |
          | |              X         |
          | |                X       |
          | |                  X     |
          | |                    X   |
          | |                      X |
          +--------------------------+
          0                          1
           Returned threshold
    '''

    @staticmethod
    def get_max_threshold_for_max_attr(perfs_list: List[perf_datastruct.Perf],
                                       attribute: str) -> (float, float):
        """
        Work on a decreasing graph ONLY !
        Find max on the graph
        :param perfs_list: List of object (Perf object)
        :param attribute: Which attribute of the object in the object list to look for : TP,TN,FP,FN, ...
        :return: The threshold and the value of the max of the graph
        """
        threshold, max_value = Calibrator._get_initial_values(perfs_list, attribute)

        # Dummy max search
        for curr_perf in perfs_list:
            curr_value = getattr(curr_perf.score, attribute)
            if curr_value >= max_value:
                threshold = curr_perf.threshold

        return threshold, max_value

    '''
            +--------------------------+
   returned |X       way of iteration  |
   value    |  X       +------->       |
            |    X                     |
            |      X                   |
            |        X                 |
            |          X               |
            |            X             |
            |              X           |
            |                X         |
            |                  X       |
            |                    X     |
            |                      X   |
            |                     ^  X |
            +---------------------+----+
            0                        1
                                Returned threshold
    '''

    @staticmethod
    def get_min_threshold_for_min_attr(perfs_list: List[perf_datastruct.Perf], attribute: str) -> (float, float):
        """
        Work on a decreasing graph ONLY !
        Find max on the graph
        :param perfs_list: List of object (Perf object)
        :param attribute: Which attribute of the object in the object list to look for : TP,TN,FP,FN, ...
        :return: The threshold and the value of the min of the graph
        """
        threshold, max_value = Calibrator._get_initial_values(perfs_list, attribute)

        # Dummy min search
        for curr_perf in perfs_list:
            curr_value = getattr(curr_perf.score, attribute)
            if curr_value <= max_value:
                threshold = curr_perf.threshold

        return threshold, max_value

    @staticmethod
    def _get_initial_values(perfs_list: List[perf_datastruct.Perf], attribute: str) -> (float, float):
        """
        Get the initial value of the list (threshold and value). Performs sanity checks.
        :param perfs_list: List of object (Perf object)
        :param attribute: Which attribute of the object in the object list to look for : TP,TN,FP,FN, ...
        :return: the first threshold and value of the list. Check for sanity
        """

        # Sanity check
        if len(perfs_list) > 0:
            max_value = getattr(perfs_list[0].score, attribute)
            threshold = perfs_list[0].threshold

            # Check if graph is decreasing
            if len(perfs_list) > 1:
                first_val = getattr(perfs_list[0].score, attribute)
                last_val = getattr(perfs_list[len(perfs_list) - 1].score, attribute)

                if first_val < last_val and attribute != "F1":
                    raise Exception("Graph is not decreasing ! Impossible to compute on such graph without heavy artifacts and unknown outputs. Aborting.")

            return threshold, max_value
        else:
            raise Exception("Empty list of perf objects.")

    # =================== Optimizer for one value ===================

    def get_threshold_where_upper_are_less_than_xpercent_FN(self, perfs_list: List[perf_datastruct.Perf], percent: float):
        """
        Visualisation of goal
            +-------------------------------------+
            |X   TNR                              |
            | XXX                                 X
            |   XXX                               |
            |     XXX                     +       |
            |       XXX                   |       |
            |         XXX                 |       |
            |           XXX               |       |
            |             XXXX            |       |
            |                XXXX         |       |
            |                   XXXXX     v       |
            |                       XXXXXX        |
            |                            XXXXXXX  |
            |                             FNR  XXX|
            +-------------------------------------+
        Minimum value of a decreasing graph, while minimizing threshold.
        upper to this threshold, there is less than X percent of false negative
        3 = leftmost lower (decreasing) = leftmost higher (increasing)
        :param perfs_list:
        :param percent:
        :return:
        """
        #
        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="FNR",
                                                        higher=False,
                                                        rightmost=False,
                                                        is_increasing=False,
                                                        tolerance=percent)

    def get_threshold_where_upper_are_more_than_xpercent_TP(self, perfs_list: List[perf_datastruct.Perf], percent: float):
        """
        Visualisation of goal
           +-------------------------------------+
           |                                TPR  |
           |                              XXXXXXXX
           |                           XXXX      |
           |                         XXX    ^    |
           |                      XXXX      |    |
           |                  XXXXX         |    |
           |                XXX             |    |
           |             XXXX               |    |
           |          XXXX                  |    |
           |       XXXX                     |    |
           |     XXX                        |    |
           | XXXXX                          |    |
           |XX  FPR                         |    |
           +--------------------------------+----+
        Maximizing value of an increasing graph, while minimizing threshold
        upper to this threshold, there is more than X percent of true positive
        2 = righmost higher (decreasing) = righmost lower (increasing)
        :param perfs_list:
        :param percent:
        :return:
        """

        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="TPR",
                                                        higher=False,
                                                        rightmost=True,
                                                        is_increasing=True,
                                                        tolerance=percent)

    def get_threshold_where_below_are_more_than_xpercent_TN(self, perfs_list: List[perf_datastruct.Perf], percent: float):
        """
        Visualisation of goal
         +-------------------------------------+
         |X   TNR                              |
         | XXX                                 X
         |   XXX                               |
         |     XXX                             |
         |       XXX                           |
         |     ^   XXX                         |
         |     |     XXX                       |
         |     |       XXXX                    |
         |     |          XXXX                 |
         |     |             XXXXX             |
         |     |                 XXXXXX        |
         |     |                      XXXXXXX  |
         |     |                       FNR  XXX|
         +-----+-------------------------------+
        Maximizing value of a decreasing graph, while Maximizing threshold
        below to this threshold, there is more than X percent of true negative
        2 = righmost higher (decreasing) = righmost lower (increasing)
        :param perfs_list:
        :param percent:
        :return:
        """

        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="TNR",
                                                        higher=True,
                                                        rightmost=True,
                                                        is_increasing=False,
                                                        tolerance=percent)

    def get_threshold_where_below_are_less_than_xpercent_FP(self, perfs_list: List[perf_datastruct.Perf], percent: float):
        """
        Visualisation of goal
          +-------------------------------------+
          |                                TPR  |
          |                              XXXXXXXX
          |                           XXXX      |
          |                         XXX         |
          |                      XXXX           |
          |                  XXXXX              |
          |                XXX                  |
          |             XXXX                    |
          |          XXXX                       |
          |       XXXX                          |
          |     XXX  ^                          |
          | XXXXX    |                          |
          |XX  FPR   |                          |
          +----------+--------------------------+
        Minimizing value of an increasing graph, while maximizing threshold
        below to this threshold, there is less than X percent of false positive
        3 = leftmost lower (decreasing) = leftmost higher (increasing)
        :param perfs_list:
        :param percent:
        :return:
        """

        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="FPR",
                                                        higher=True,
                                                        rightmost=False,
                                                        is_increasing=True,
                                                        tolerance=percent)

    def get_max_threshold_for_max_F1(self, perfs_list: List[perf_datastruct.Perf]):
        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="F1",
                                                        higher=True,
                                                        rightmost=True,
                                                        is_increasing=True)


def default_conf(args):
    cal_conf = calibrator_conf.Default_calibrator_conf.get_default_instance()
    return cal_conf


def load_from_file(args):
    cal_conf = calibrator_conf.Default_calibrator_conf()
    # TODO : Load from file !
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
    parser_b.add_argument('-AFNR', dest="AFNR", type=float, action='store', help='Acceptable False Negative Rate (target)')
    parser_b.add_argument('-MTPR', dest="MTPR", type=float, action='store', help='Minimum True Positive Rate (target)')
    parser_b.add_argument('-MTNR', dest="MTNR", type=float, action='store', help='Minimum True Negative Rate (target)')
    parser_b.set_defaults(func=load_from_args)

    args = parser.parse_args()

    try:
        func = args.func
        tmp_cal_conf = func(args)
        calibrator = Calibrator()
        calibrator.set_calibrator_conf(tmp_cal_conf)
        calibrator.calibrate_douglas_quaid(folder_of_pictures=pathlib.Path(args.src),
                                           ground_truth_file=pathlib.Path(args.gt),
                                           output_folder=pathlib.Path(args.dest))

    except AttributeError as e:
        parser.error(f"Too few arguments : {e}")
