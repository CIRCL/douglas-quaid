#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging.config
import pathlib
from pprint import pformat
from typing import List, Dict

import carlhauser_client.Helpers.dict_utilities as dict_utilities
import common.ImportExport.json_import_export as json_import_export
import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
import common.PerformanceDatastructs.stats_datastruct as stats_datastruct
from carlhauser_client.API.extended_api import Extended_API
from common.Graph.graph_datastructure import GraphDataStruct
from common.environment_variable import get_homedir
from common.environment_variable import load_client_logging_conf_file
import common.Calibrator.calibrator_conf as calibrator_conf
import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures
import common.ChartMaker.two_dimensions_plot as two_dimensions_plot

load_client_logging_conf_file()


# ==================== ------ LAUNCHER ------- ====================
class similarity_graph_quality_evaluator:
    def __init__(self, cal_conf: calibrator_conf.Default_calibrator_conf):
        self.logger = logging.getLogger(__name__)
        self.ext_api = Extended_API.get_api()
        self.cal_conf = cal_conf

        '''
        self.pts_nb: int = 50
        self.min_threshold: float = 0
        self.max_threshold: float = 1

        self.NB_TO_CHECK: int = 3  # Number of first match to check to get the scores and overview
        '''

    # =================== Optimizer for one value ===================
    def get_perf_list(self, list_results: List,
                      gt_graph: GraphDataStruct,
                      output_folder: pathlib.Path = None) -> List[perf_datastruct.Perf]:
        '''
        Extract a list of performance datastructure from a list of results (list_results)
        compared to a ground truth file (gt_graph). Can store provided list and ground truth results if a (output_folder) is given.
        :param list_results: The list of results extracted from server (one result for each node of the graph)
        :param gt_graph: The ground truth file that serves as reference
        :param output_folder: Faculatative output folder to save inputs
        :return: a list of performance datastructure, each having a threshold and a stats datastructure. This means that for each computed threshold, we know the quality of the graph.
        '''

        # DEBUG purposes / Display arguments
        self.logger.debug("Received requests results :")
        self.logger.debug(pformat(list_results))
        self.logger.debug("Received ground truth graph :")
        self.logger.debug(pformat(gt_graph.export_as_dict()))

        # TODO : Remove output folder ?
        if output_folder is not None:
            # Saving ground truth graph
            json_import_export.save_json(list_results, get_homedir() / "requests_result.json")

            # Saving list results
            json_import_export.save_json(gt_graph.export_as_dict(), get_homedir() / "gt_graph.json")
        else:
            self.logger.debug("List results and ground truth graph can't be saved : no output_folder specified.")

        perfs_list = self._compute_perfs_list(list_results, gt_graph)

        return perfs_list

    def get_perf_list_decision(self, list_results: List,
                      gt_graph: GraphDataStruct,
                      output_folder: pathlib.Path):

        # Build 4 list, each filtering out all except one decision type
        self.build_list_and_evaluate_and_save_chart(list_results, gt_graph,
                                                    [scoring_datastrutures.DecisionTypes.YES], output_folder)
        self.build_list_and_evaluate_and_save_chart(list_results, gt_graph,
                                                    [scoring_datastrutures.DecisionTypes.MAYBE], output_folder)
        self.build_list_and_evaluate_and_save_chart(list_results, gt_graph,
                                                    [scoring_datastrutures.DecisionTypes.YES,
                                                     scoring_datastrutures.DecisionTypes.MAYBE], output_folder)
        self.build_list_and_evaluate_and_save_chart(list_results, gt_graph,
                                                    [scoring_datastrutures.DecisionTypes.NO], output_folder)

    def build_list_and_evaluate_and_save_chart(self , list_results : List,
                                               gt_graph: GraphDataStruct,
                                               only_decisions : List[scoring_datastrutures.DecisionTypes],
                                               output_folder: pathlib.Path):

        # Generate name of the list
        generated_name = "".join([d.name + "_" for d in only_decisions]) + "only"

        # Filter out results
        results_list_filtered = [self.filter_out_request_result(r, only_decisions) for r in list_results]
        json_import_export.save_json(results_list_filtered, pathlib.Path(get_homedir() / (generated_name + ".json")))

        perfs_list_filtered = self._compute_perfs_list(results_list_filtered, gt_graph)
        # Save to graph
        twoDplot = two_dimensions_plot.TwoDimensionsPlot()
        twoDplot.print_graph(perfs_list_filtered, output_folder, file_name=(generated_name + ".png"))

    def _compute_perfs_list(self, list_results : List, gt_graph: GraphDataStruct):
        # Init a void performance list
        perfs_list: List[perf_datastruct.Perf] = []

        # For each evaluation points
        for i in range(self.cal_conf.PTS_NB):
            # Computing the new threshold
            curr_threshold = i * ((self.cal_conf.MAX_THRESHOLD - self.cal_conf.MIN_THRESHOLD) / self.cal_conf.PTS_NB)
            self.logger.info(f"Current threshold computation : {curr_threshold}")

            # Compute score for this threshold
            # TODO : To remove the export (debug only)
            # json_import_export.save_json(list_results, pathlib.Path(get_homedir() / "result_file_to_be_evaluated.json"))
            tmp_score = self.compute_score_for_one_threshold(list_results, gt_graph, curr_threshold)
            self.logger.info(f"Current score for this threshold : {tmp_score}")

            # Store the score in the performance datastructure
            tmp_perf = perf_datastruct.Perf(tmp_score, curr_threshold)

            # Add to performance list
            perfs_list.append(tmp_perf)

        return perfs_list

    @staticmethod
    def filter_out_request_result(request : Dict, only_decisions : List[scoring_datastrutures.DecisionTypes]):
        # DOES NOT MODIFY REQUEST OBJECT ANY LONGER !

        filtered_matches = []
        new_request = request.copy()

        '''
        new_request["list_cluster"] = request["list_cluster"]
        new_request["list_pictures"] = request["list_pictures"]
        new_request["request_id"] = request["request_id"]
        new_request["status"] = request["status"]
        '''

        # Transform decision in string
        tmp_decision_names = [d.name for d in only_decisions]

        # Filter out each match which is not in the provided decisions list
        for match in new_request.get("list_pictures", []):
            if match["decision"] in tmp_decision_names:
                filtered_matches.append(match)

        # Put it back in place in the request dict
        new_request["list_pictures"] = filtered_matches

        return new_request

    @staticmethod
    def is_correct(result: Dict):
        '''
        Checks if a request result is valid to be evaluated.
        Check if it has enough matches, if correctly formatted ...
        :param result: One request result from server
        :return: True if correct, Error if problem
        '''

        if result.get("request_id", None) is None:
            print(pformat(result))
            raise Exception("Request id not set in requests result. Please review data set ?")
        elif result.get("list_pictures", None) is None:

            if result.get("status",None) == "matches_not_found" :
                # No pictures matched :
                return False
            else :
                print(pformat(result))
                raise Exception("No matched list of picture in requests result.")

        elif len(result.get("list_pictures")) == 0:
            print(pformat(result))
            return False
            # raise Exception("No matched for current picture in requests result.")
            # TODO : Same as upper case

        return True

    def compute_score_for_one_threshold(self, list_results: List,
                                        gt_graph: GraphDataStruct,
                                        dist_threshold: float) -> stats_datastruct.Stats_datastruct:
        '''
        Compute stats about the quality of a result (requests_result), given a specific threshold (dist_threshold)
        and compared to a ground truth graph (gt_graph)
        :param list_results: Result of a similarity request to server
        :param gt_graph: Ground truth file to provide to compute if matches are good or not
        :param dist_threshold: threshold to apply to the results to compare to ground truth graph
        :return: stats about the quality of a result
        '''

        # Create ready to go (with 0 valued) score object
        tmp_score = stats_datastruct.Stats_datastruct()
        tmp_score.reset_basics_values()

        # TODO : Construct good datastructure to perform the matching
        # Sort cand_graph to mapping [node.id] -> [node.id sorted by distance increasing]

        # For each node and its neighbourhood (by distance)
        for curr_result in list_results:

            # Check if node is correctly formatted
            if self.is_correct(curr_result):

                # Remove its own occurence from the list if presents.
                matches_list = dict_utilities.get_clear_matches(curr_result)

                # For all N first matches of the current picture (or below if less matches)
                nb_matches_to_process = min(self.cal_conf.NB_TO_CHECK, len(matches_list))

                for i in range(0, nb_matches_to_process):
                    # fetch the match to process
                    curr_matched_node = matches_list[i]

                    # Please note :
                    # If the two nodes are in the same cluster in gt, then it should be a positive value.
                    # Then this link is counted as a positive value in the entire dataset.
                    # The distance and threshold DOES NOT IMPACT the Positive/Negative counts !

                    if curr_matched_node.get("distance") <= dist_threshold:
                        # Even if it's request_id, it the current name of the file.
                        if gt_graph.are_names_in_same_cluster(curr_result.get("request_id"), curr_matched_node.get("image_id")):
                            tmp_score.TP += 1   # Match but good
                            tmp_score.P += 1    # Should be good

                        else:
                            tmp_score.FP += 1   # No match but not good
                            tmp_score.N += 1    # Should be not good

                    elif curr_matched_node.get("distance") > dist_threshold:

                        # Even if it's request_id, it the current name of the file.
                        if gt_graph.are_names_in_same_cluster(curr_result.get("request_id"), curr_matched_node.get("image_id")):
                            tmp_score.FN += 1   # No match but not good
                            tmp_score.P += 1    # Should be good

                        else:
                            tmp_score.TN += 1   # No match but good
                            tmp_score.N += 1    # Should be not good

            else :
                cluster = gt_graph.get_clusters_of(curr_result.get("request_id"))

                if cluster is None or len(cluster.members) <= 1:
                    # this picture has no cluster OR Only one element in the cluster,
                    # so it's the node = Good if no match
                    tmp_score.TN += 1   # No match but good
                    tmp_score.N += 1    # Should be not good
                else:
                    # No matches, but not alone in the cluster, so should have been one.
                    tmp_score.FN += 1   # No match but not good
                    tmp_score.P += 1    # Should be good

            tmp_score.total_nb_elements = tmp_score.P + tmp_score.N
            tmp_score.compute_in_good_order()

        return tmp_score

