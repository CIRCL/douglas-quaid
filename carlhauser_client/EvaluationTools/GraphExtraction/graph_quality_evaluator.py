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
from common.ImportExport.json_import_export import save_json
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.edge import Edge
from common.Graph.node import Node

import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
import common.PerformanceDatastructs.stats_datastruct as stats_datastruct

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class GraphQualityEvaluator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ext_api = Extended_API.get_api()

        self.pts_nb = 50
        self.min_threshold = 0
        self.max_threshold = 1

    def evaluate_performance(self, cand_graph: GraphDataStruct, gt_graph: GraphDataStruct) -> List[perf_datastruct.Perf]:
        self.logger.debug("Received candidate graph :")
        self.logger.debug(cand_graph.export_as_dict())
        self.logger.debug("Received ground truth graph :")
        self.logger.debug(gt_graph.export_as_dict())

        scores_perfs  : List[perf_datastruct.Perf] = []
        for i in range(self.pts_nb):

            # Computing the new threshold
            curr_threshold = i * ((self.max_threshold - self.min_threshold) / self.pts_nb)
            self.logger.info(f"Current threshold computation : {curr_threshold}")

            tmp_score = self.compute_score_for_one_threshold(cand_graph, gt_graph, curr_threshold)
            tmp_perf = perf_datastruct.Perf(tmp_score, curr_threshold)

            # Add to performance list
            scores_perfs.append(tmp_perf)

            '''
            # Choose a configuration
            # Put configuration in place
            if self.server_launcher is not None:
                del self.server_launcher
            self.server_launcher = core.launcher_handler()
            self.server_launcher.di_conf.MAX_DIST_FOR_NEW_CLUSTER = curr_threshold
            '''

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

            '''
            # Create output folder for this configuration
            tmp_output = output_folder / ''.join([str(curr_threshold), "_threshold"])
            tmp_output.mkdir(parents=True, exist_ok=True)
            '''

        return scores_perfs


    def compute_score_for_one_threshold(self, cand_graph: GraphDataStruct, gt_graph: GraphDataStruct, dist_threshold : float)-> stats_datastruct.Stats_datastruct:
        # Create ready to go (with 0 values) score object
        tmp_score = stats_datastruct.Stats_datastruct()
        tmp_score.reset_basics_values()

        # For each node and its neighbours (by distance)

        self.logger.debug(cand_graph)
        self.logger.debug(gt_graph)
        save_json(cand_graph.export_as_dict(), pathlib.Path("./cand_graph.json"))
        save_json(gt_graph.export_as_dict(), pathlib.Path("./gt_graph.json"))



        # TODO : Construct good datastructure to perform the matching
        # Sort cand_graph to mapping [node.id] -> [node.id sorted by distance increasing]


        '''
        

        # For each first link = first match, find the
        for node in cand_graph.nodes :
            if node.id in gt_graph.clusters.get(cand_gr) :



            # For each pair : node and best match

            if curr_dist < dist_threshold :
                tmp_score.P += 1

                if curr_candidate_node.is_in_same_cluster_as(curr_candidate_node.best_match) :
                    tmp_score.TP += 1
                else :
                    tmp_score.FP += 1

            if curr_dist > dist_threshold :
                tmp_score.N += 1

                if curr_candidate_node.is_in_same_cluster_as(curr_candidate_node.best_match) :
                    tmp_score.FN += 1
                else:
                    tmp_score.TN += 1

        '''

        return tmp_score
