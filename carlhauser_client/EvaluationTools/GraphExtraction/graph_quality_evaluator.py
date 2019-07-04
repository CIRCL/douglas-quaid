#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
from carlhauser_client.API.extended_api import Extended_API
from common.Graph.graph_datastructure import GraphDataStruct

import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
import common.PerformanceDatastructs.stats_datastruct as stats_datastruct
import common.ImportExport.json_import_export as json_import_export

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class GraphQualityEvaluator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ext_api = Extended_API.get_api()

        self.pts_nb: int = 50
        self.min_threshold: float = 0
        self.max_threshold: float = 1

        self.NB_TO_CHECK: int = 3  # Number of first match to check to get the scores and overview
        self.TOLERANCE: float = 0.1  # [0-1] acceptable drop of True Positive and increase of False Negative

    # =================== Optimizer for one value ===================
    def get_max_TP(self, perfs_list: List[perf_datastruct.Perf]):

        if len(perfs_list) == 0:
            raise Exception("Performance list void ! Impossible to get max True Positive threshold")

        # We could have assumed the performance list is sorted
        perfs_list.sort(key=lambda k: k.threshold)
        self.logger.debug(f"Threshold list : {[p.threshold for p in perfs_list]}")
        self.logger.debug(f"TPR list : {[p.score.TPR for p in perfs_list]}")
        self.logger.debug(f"Minimum TPR allowed : {1 - self.TOLERANCE}")

        max_TPR = perfs_list[0].score.TPR
        threshold_max_for_max_TPR = perfs_list[0].threshold

        for curr_perf in perfs_list:
            self.logger.debug(f"Current best threshold : {threshold_max_for_max_TPR}")
            self.logger.debug(f"Current best performance : {max_TPR}")
            self.logger.debug(f"Current threshold compared : {curr_perf.threshold}")
            self.logger.debug(f"Current performance compared : {curr_perf.score.TPR}")

            # While the TPR is not lowered AND the TPR is upper than the limit ...
            if curr_perf.score.TPR >= max_TPR or curr_perf.score.TPR >= (1 - self.TOLERANCE):
                # We found a new higher threshold where the TPR is still as high as before OR
                # Which is still high enough in the tolerance interval
                threshold_max_for_max_TPR = curr_perf.threshold
                max_TPR = curr_perf.score.TPR
            else:
                # We have "gone to down in the graph" and should stop here
                break

        return threshold_max_for_max_TPR

    def get_min_FP(self, perfs_list: List[perf_datastruct.Perf]):

        if len(perfs_list) == 0:
            raise Exception("Performance list void ! Impossible to get min FalseNegative threshold")

        # We could have assumed the performance list is sorted
        perfs_list.sort(key=lambda k: k.threshold, reverse=True)

        threshold_max_for_max_FPR = perfs_list[0].score.TPR

        for curr_perf in perfs_list:
            if curr_perf.score.FPR >= threshold_max_for_max_FPR or curr_perf.score.FPR > (1 - self.TOLERANCE):
                # We found a new higher threshold where the TPR is still as high as before OR
                # Which is still high enough in the tolerance interval
                threshold_max_for_max_FPR = curr_perf.score.FPR
            else:
                # We have "gone to down in the graph" and should stop here
                break

        return threshold_max_for_max_FPR

    def get_mean(self, perfs_list: List[perf_datastruct.Perf]):
        return 0

    '''
        if len(perfs_list) == 0 :
            raise Exception("Performance list void ! Impossible to get mean threshold for TruePositive and FalseNegative equilibrium")

        threshold_mean_for_equilibrium_TP_TN = perfs_list[0].score.TP

        for curr_perf in perfs_list :
            if curr_perf.score.TP >=
            threshold_max_for_max_TP =

        return threshold_mean_for_equilibrium_TP_TN
    '''

    # =================== Optimizer for one value ===================
    def get_perf_list(self, requests_result: List, gt_graph: GraphDataStruct) -> List[perf_datastruct.Perf]:
        # DEBUG #
        self.logger.debug("Received requests results :")
        self.logger.debug(requests_result)
        json_import_export.save_json(requests_result, get_homedir() / "requests_result.json")
        self.logger.debug("Received ground truth graph :")
        self.logger.debug(gt_graph.export_as_dict())
        json_import_export.save_json(gt_graph.export_as_dict(), get_homedir() / "gt_graph.json")

        # Create void perfs list
        perfs_list: List[perf_datastruct.Perf] = []
        for i in range(self.pts_nb):
            # Computing the new threshold
            curr_threshold = i * ((self.max_threshold - self.min_threshold) / self.pts_nb)
            self.logger.info(f"Current threshold computation : {curr_threshold}")

            tmp_score = self.compute_score_for_one_threshold(requests_result, gt_graph, curr_threshold)
            tmp_perf = perf_datastruct.Perf(tmp_score, curr_threshold)

            # Add to performance list
            perfs_list.append(tmp_perf)

        return perfs_list

    def compute_score_for_one_threshold(self, requests_result: List, gt_graph: GraphDataStruct, dist_threshold: float) -> stats_datastruct.Stats_datastruct:
        # Create ready to go (with 0 valued) score object
        tmp_score = stats_datastruct.Stats_datastruct()
        tmp_score.reset_basics_values()

        # For each node and its neighbours (by distance)
        # TODO : Construct good datastructure to perform the matching
        # Sort cand_graph to mapping [node.id] -> [node.id sorted by distance increasing]

        for curr_node in requests_result:

            if curr_node.get("request_id", None) is None:
                raise Exception("Request id not set in requests result. Please review data set ?")
            elif curr_node.get("list_pictures", None) is None:
                raise Exception("No matched list of picture in requests result.")
                # TODO : No pictures matched : check if alone in gt in his cluster, if so, good. Does not participate to score ?
            elif len(curr_node.get("list_pictures")) == 0:
                raise Exception("No matched for current picture in requests result.")
                # TODO : Same as upper case
            else:
                # Everything's fine, normal case

                # Remove its own occurence from the list if presents.
                matches_list = [m for m in curr_node.get("list_pictures") if m.get("image_id") != curr_node.get("request_id")]

                # For all N first matches of the current picture (or below if less matches)
                nb_matches_to_process = min(self.NB_TO_CHECK, len(matches_list))

                for i in range(0, nb_matches_to_process):
                    curr_matched_node = matches_list[i]

                    # Please note : If the two nodes are in the same cluster in gt, then it should be a positive value.
                    # Then this link is counted as a positive value in the entire dataset.
                    # The distance and threshold DOES NOT IMPACT the Positive/Negative counts !
                    if curr_matched_node.get("distance") < dist_threshold:

                        if gt_graph.are_in_same_cluster(curr_node.get("request_id"), curr_matched_node.get("image_id")):
                            tmp_score.TP += 1
                            tmp_score.P += 1

                        else:
                            tmp_score.FP += 1
                            tmp_score.N += 1

                    if curr_matched_node.get("distance") > dist_threshold:

                        if gt_graph.are_in_same_cluster(curr_node.get("request_id"), curr_matched_node.get("image_id")):
                            tmp_score.FN += 1
                            tmp_score.P += 1

                        else:
                            tmp_score.TN += 1
                            tmp_score.N += 1

            tmp_score.total_nb_elements = tmp_score.P + tmp_score.N
            tmp_score.compute_in_good_order()
        return tmp_score
