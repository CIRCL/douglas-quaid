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

    def get_optimal_for_optimized_attribute(self, perfs_list: List[perf_datastruct.Perf], attribute: str, maximize_threshold: bool = True, maximize_attribute=False, is_increasing: bool = True, tolerance: float = 0.1):
        # Extract the threshold for a specific kind of value
        # Max threshold, Max attribute = Get the rightmost higher value of the attribute
        # Max threshold, Min attribute = Get the rightmost lower value of the attribute, with attribute > Tolerance of the graph_evaluator
        # Min threshold, Max attribute = Get the leftmost higher value of the attribute, with attribute < Tolerance of the graph_evaluator
        # Min threshold, Min attribute = Get the leftmost lower value of the attribute
        # is_increasing define if the graph is going up and up or not.

        if len(perfs_list) == 0:
            raise Exception("Performance list empty ! Impossible to get threshold out of it.")

        # We could have assumed the performance list is sorted
        perfs_list.sort(key=lambda k: k.threshold, reverse=is_increasing)
        if not is_increasing :
            maximize_threshold = not maximize_threshold
            maximize_attribute = not maximize_attribute
        # We want a decreasing graph, always.
        '''
        l = [1,2,5,3,7]
        l.sort() = [1, 2, 3, 5, 7]
        '''

        self.logger.debug(f"Threshold list : {[p.threshold for p in perfs_list]}")
        self.logger.debug(f"Perf list : {[getattr(p.score, attribute) for p in perfs_list]}")

        if maximize_threshold and maximize_attribute:
            return self.get_max_threshold_for_max_attr(perfs_list, attribute)

        elif maximize_threshold is False and maximize_attribute:
            self.logger.debug(f"Minimum {attribute} allowed : {1 - self.TOLERANCE}")
            return self.get_min_threshold_for_max_attr_with_tolerance(perfs_list, attribute, 1 - self.TOLERANCE)

        elif maximize_threshold and maximize_attribute is False:
            self.logger.debug(f"Minimum {attribute} allowed : {self.TOLERANCE}")
            return self.get_min_threshold_for_max_attr_with_tolerance(perfs_list, attribute, self.TOLERANCE)

        elif maximize_threshold is False and maximize_attribute is False:
            return self.get_min_threshold_for_min_attr(perfs_list, attribute)

    @staticmethod
    def get_min_threshold_for_max_attr_with_tolerance(perfs_list: List[perf_datastruct.Perf], attribute: str, tolerance: float) -> (float, float):
        max_value = getattr(perfs_list[0].score, attribute)
        threshold = perfs_list[0].threshold
        # Work on a decreasing graph ONLY !
        # Dummy constraint search. At the point where the constraint (be above the threshold) is borken, we break and return the found values.
        for curr_perf in perfs_list:
            curr_value = getattr(curr_perf.score, attribute)
            if curr_value >= tolerance:
                threshold = curr_perf.threshold
            else:
                break

        return threshold, max_value

    @staticmethod
    def get_max_threshold_for_max_attr(perfs_list: List[perf_datastruct.Perf], attribute: str) -> (float, float):
        max_value = getattr(perfs_list[0].score, attribute)
        threshold = perfs_list[0].threshold

        # Dummy max search
        for curr_perf in perfs_list:
            curr_value = getattr(curr_perf.score, attribute)
            if curr_value >= max_value:
                threshold = curr_perf.threshold

        return threshold, max_value

    @staticmethod
    def get_min_threshold_for_min_attr(perfs_list: List[perf_datastruct.Perf], attribute: str) -> (float, float):
        max_value = getattr(perfs_list[0].score, attribute)
        threshold = perfs_list[0].threshold

        # Dummy min search
        for curr_perf in perfs_list:
            curr_value = getattr(curr_perf.score, attribute)
            if curr_value <= max_value:
                threshold = curr_perf.threshold

        return threshold, max_value

    # =================== Optimizer for one value ===================

    # get_x_percent_FN_min_threshold
    def get_threshold_where_upper_are_less_than_xpercent_FN(self, perfs_list: List[perf_datastruct.Perf], percent : float):
        # upper to this threshold, there is less than X percent of false negative
        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="FNR",
                                                        maximize_attribute=True,
                                                        maximize_threshold=False,
                                                        is_increasing=False,
                                                        tolerance = percent)

    # get_x_percent_TP_min_threshold
    def get_threshold_where_upper_are_more_than_xpercent_TP(self, perfs_list: List[perf_datastruct.Perf], percent : float):
        # upper to this threshold, there is more than X percent of true positive

        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="TPR",
                                                        maximize_attribute=True,
                                                        maximize_threshold=False,
                                                        is_increasing=True,
                                                        tolerance = percent)
    # get_x_percent_TN_max_threshold
    def get_threshold_where_below_are_more_than_xpercent_TN(self, perfs_list: List[perf_datastruct.Perf], percent : float):
        # below to this threshold, there is more than X percent of true negative

        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="TNR",
                                                        maximize_attribute=False,
                                                        maximize_threshold=True,
                                                        is_increasing=False,
                                                        tolerance = percent)
    # get_x_percent_FP_max_threshold
    def get_threshold_where_below_are_less_than_xpercent_FP(self, perfs_list: List[perf_datastruct.Perf], percent : float):
        # below to this threshold, there is less than X percent of false positive

        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="FPR",
                                                        maximize_attribute=False,
                                                        maximize_threshold=True,
                                                        is_increasing=True,
                                                        tolerance = percent)

    '''
    def get_min_threshold_for_max_TPR(self, perfs_list: List[perf_datastruct.Perf]):
        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="TPR",
                                                        maximize_attribute=True,
                                                        maximize_threshold=False,
                                                        is_increasing=True)

    def get_max_threshold_for_min_TNR(self, perfs_list: List[perf_datastruct.Perf]):
        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="TNR",
                                                        maximize_attribute=False,
                                                        maximize_threshold=True,
                                                        is_increasing=False)
    '''

    def get_max_threshold_for_max_F1(self, perfs_list: List[perf_datastruct.Perf]):
        return self.get_optimal_for_optimized_attribute(perfs_list=perfs_list,
                                                        attribute="F1",
                                                        maximize_attribute=True,
                                                        maximize_threshold=True,
                                                        is_increasing=True)

    def get_mean(self, perfs_list: List[perf_datastruct.Perf]):
        return 0

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

                        if gt_graph.are_names_in_same_cluster(curr_node.get("request_id"), curr_matched_node.get("image_id")):  # Even if it's request_id, it the current name of the file.
                            tmp_score.TP += 1
                            tmp_score.P += 1

                        else:
                            tmp_score.FP += 1
                            tmp_score.N += 1

                    if curr_matched_node.get("distance") > dist_threshold:

                        if gt_graph.are_names_in_same_cluster(curr_node.get("request_id"), curr_matched_node.get("image_id")):  # Even if it's request_id, it the current name of the file.
                            tmp_score.FN += 1
                            tmp_score.P += 1

                        else:
                            tmp_score.TN += 1
                            tmp_score.N += 1

            tmp_score.total_nb_elements = tmp_score.P + tmp_score.N
            tmp_score.compute_in_good_order()
        return tmp_score
