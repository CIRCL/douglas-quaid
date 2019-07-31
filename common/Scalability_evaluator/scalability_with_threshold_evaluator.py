#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
from typing import List

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import common.Scalability_evaluator.scalability_conf as scalability_conf
from common.Scalability_evaluator.scalability_evaluator import ScalabilityData, ScalabilityEvaluator
# from carlhauser_server.Configuration.distance_engine_conf import Default_distance_engine_conf
from common.environment_variable import dir_path
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class ScalabilityEvaluatorWithThreshold(ScalabilityEvaluator):

    def __init__(self, tmp_scalability_conf=scalability_conf.Default_scalability_conf()):
        super().__init__(tmp_scalability_conf)

    def evaluate_scalability_with_threshold(self,
                                            pictures_folder: pathlib.Path,
                                            output_folder: pathlib.Path,
                                            nbiter: int) -> List[ScalabilityData]:
        # Put TOTAL-X pictures into boxes (10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000 ...)
        # Generate the boxes
        # list_boxes_sizes = self.scalability_conf.generate_boxes(self.scalability_conf.MAX_NB_PICS_TO_SEND)
        list_boxes_sizes = self.scalability_conf.generate_boxes_linear(self.scalability_conf.MAX_NB_PICS_TO_SEND)

        nb_pts = nbiter
        min_thre = 0.01
        max_thre = 0.4

        # TODO : Factorize axis iteration in one function, already used in calibrator.
        list_scalability_data = []
        for i in range(nb_pts):
            # ==== Separate the folder files ====
            pictures_set = self.load_pictures(pictures_folder)
            # Ex :  Load the list of XXX pictures

            # Extract X pictures to evaluate their matching (at each cycle, the sames)
            # TODO : REMOVED FOR NOW. SHOULD BE ABLE TO DELETE RESULTS TO WORK. #pictures_set, pics_to_evaluate = self.biner(pictures_set, self.scalability_conf.NB_PICS_TO_REQUEST)
            self.logger.info(f"Nb of pictures to be uploaded in many passes : {len(pictures_set)}")
            # TODO : REMOVED FOR NOW. SHOULD BE ABLE TO DELETE RESULTS TO WORK. #self.logger.info(f"Nb of pictures to request : {len(pics_to_evaluate)}")
            # Ex :  XXX pictures to use later + 10 pictures to request

            # Computing the new threshold
            curr_threshold = i * ((max_thre - min_thre) / nb_pts)
            self.logger.info(f"Current threshold scalability test : {curr_threshold}")

            # Generate configuration file
            dist_conf = distance_engine_conf.Default_distance_engine_conf()
            dist_conf.MAX_DIST_FOR_NEW_CLUSTER = curr_threshold
            # fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

            # ==== Upload pictures + Make requests ====
            scalability_data = self.get_scalability_list(list_boxes_sizes, pictures_set, dist_conf=dist_conf) # pics_to_evaluate,
            scalability_data.threshold_cluster = curr_threshold
            self.logger.info(f"Scalability data : {scalability_data}")

            # Create folder and store data
            curr_output_folder = output_folder / ("threshold_" + str(curr_threshold))
            curr_output_folder.mkdir(exist_ok=True)
            self.print_data(scalability_data, curr_output_folder)

            # List of scalability data, tidying up
            list_scalability_data.append(scalability_data)

        return list_scalability_data


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch DouglasQuaid Scalability Evaluator on your own dataset to get custom scalability measure. Evaluate many different thresholds.')
    parser.add_argument("-s", '--source_path', dest="src", required=True, type=dir_path, action='store',
                        help='Source path of folder of pictures to evaluate. Should be a subset of your production data.')
    parser.add_argument("-d", '--dest_path', dest="dest", required=True, type=dir_path, action='store',
                        help='Destination path to store results of the evaluation (configuration files generated, etc.)')
    parser.add_argument("-n", '--nb_iter', dest="nbiter", required=True, type=int, action='store',
                        help='Nb of different threshold to test')
    args = parser.parse_args()

    try:
        scalability_evaluator = ScalabilityEvaluatorWithThreshold()
        scalability_evaluator.evaluate_scalability_with_threshold(pathlib.Path(args.src), pathlib.Path(args.dest), args.nbiter)

    except AttributeError as e:
        parser.error(f"Too few arguments : {e}")
