#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from typing import Dict

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.scoring_datastrutures as sd


class Merging_Engine:
    def __init__(self, db_conf: database_conf.Default_database_conf, dist_conf: distance_engine_conf.Default_distance_engine_conf, fe_conf: feature_extractor_conf.Default_feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Distance ORB Engine")

        # Save configuration
        self.db_conf = db_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.dist_conf = dist_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.fe_conf = fe_conf

        # TODO : Properly handle enum passed by file. Maybe https://stackoverflow.com/questions/22562425/attributeerror-cant-set-attribute-in-python ?
        self.distance_merging_method = feature_extractor_conf.Distance_MergingMethod[self.fe_conf.DISTANCE_MERGING_METHOD]
        self.decision_merging_method = feature_extractor_conf.Decision_MergingMethod[self.fe_conf.DECISION_MERGING_METHOD]

    # ==================== ------ PICTURE-PICTURE DISTANCE ------- ====================

    def merge_algos_distance(self, matches_package: Dict[str, sd.AlgoMatch]):
        # TODO : Complete merging / Improve
        self.logger.info(f"Received algorithms distance to merge {matches_package}")

        if self.distance_merging_method == feature_extractor_conf.Distance_MergingMethod.MAX:
            score = self.get_max_dict(matches_package)

        elif self.distance_merging_method == feature_extractor_conf.Distance_MergingMethod.MIN:
            score = self.get_min_dict(matches_package)

        elif self.distance_merging_method == feature_extractor_conf.Distance_MergingMethod.MEAN:
            score = self.get_mean_dict(matches_package)

        elif self.distance_merging_method == feature_extractor_conf.Distance_MergingMethod.WEIGHTED_MEAN:
            score = self.get_weighted_mean_dict(matches_package)

        elif self.distance_merging_method == feature_extractor_conf.Distance_MergingMethod.HARMONIC_MEAN:
            score = self.get_harmonic_mean_dict(matches_package)

        else:
            raise Exception("Unrecognized merging method to merge algorithm output into one value. Please review configuration file.")

        return score

    def merge_algos_decision(self, matches_package: Dict[str, sd.AlgoMatch]):
        # TODO : Complete merging / Improve
        self.logger.info(f"Received algorithms distance to merge {matches_package}")

        if self.decision_merging_method == feature_extractor_conf.Decision_MergingMethod.PARETO:
            score = self.get_pareto_decision(matches_package)

        elif self.decision_merging_method == feature_extractor_conf.Decision_MergingMethod.MAJORITY:
            score = self.get_majority_decision(matches_package)

        elif self.decision_merging_method == feature_extractor_conf.Decision_MergingMethod.WEIGHTED_DECISION:
            score = self.get_weighted_majority_decision(matches_package)

        else:
            raise Exception("Unrecognized merging method to merge algorithm output into one value. Please review configuration file.")

        return score

    # ==================== ------ PICTURE-CLUSTER DISTANCE ------- ====================

    def merge_pictures_distance(self, distance_list: list):
        # TODO : Complete merging / Improve
        self.logger.info(f"Received picture-cluster's picture distance to merge {distance_list}")
        if len(distance_list) != 0:
            return max(distance_list)
        else:
            self.logger.error(f"A Cluster is empty but exists. Structural behavior error detected.")
            return None

    # ==================== ------ CLUSTER-CLUSTER DISTANCE ------- ====================

    # ==================== ------ COMMON (DISTANCE) ------- ====================
    @staticmethod
    def get_max_dict(matches_package: Dict[str, sd.AlgoMatch]) -> float:
        return max([algomatch.distance for algomatch in matches_package.values()])

    @staticmethod
    def get_min_dict(matches_package: Dict[str, sd.AlgoMatch]) -> float:
        return min([algomatch.distance for algomatch in matches_package.values()])

    @staticmethod
    def get_mean_dict(matches_package: Dict[str, sd.AlgoMatch]) -> float:
        return sum([algomatch.distance for algomatch in matches_package.values()]) / len(matches_package.values())

    def get_weighted_mean_dict(self, matches_package: Dict[str, sd.AlgoMatch]) -> float:
        sum_score = 0
        sum_weight = 0
        self.logger.debug(f"Algo list {self.fe_conf.list_algos}.")
        self.logger.debug(f"Full config {self.fe_conf}.")

        for curr_algo in self.fe_conf.list_algos:
            self.logger.debug(f"Current algo {curr_algo}.")

            # We have a value for a computed algorithm
            curr_score = matches_package.get(curr_algo.get("algo_name"))
            if curr_score is not None:
                # We add the score of this algorithm
                sum_score += curr_score.distance * curr_algo.get("distance_weight")
                # We add the weight of this algorithm
                sum_weight += curr_algo.get("distance_weight")

        if sum_weight != 0:
            return sum_score / sum_weight
        else:
            raise Exception("Impossible to compute a weighted mean during algorithms outputs merging : \n"
                            "Did you put a not-null weight for activated algorithm ? Did you activated at least one algorithm ?")

    def get_harmonic_mean_dict(self, matches_package: Dict[str, sd.AlgoMatch]) -> float:
        # TODO !
        return 0

    # TODO : 90% MAX ?

    # ==================== ------ COMMON (DECISION) ------- ====================
    def get_pareto_decision(self, matches_package: Dict[str, sd.AlgoMatch]) -> sd.DecisionTypes:
        tmp_decisions = self.get_nb_decisions(matches_package)
        nb_decisions = sum(tmp_decisions.values())

        # If a decision is more than 80% of all decision, return it.
        for curr_decision in sd.DecisionTypes :
            if tmp_decisions[curr_decision.name] > 0.8*nb_decisions :
                return curr_decision
        # else, return maybe
        return sd.DecisionTypes.MAYBE

    def get_majority_decision(self, matches_package: Dict[str, sd.AlgoMatch]) -> sd.DecisionTypes:
        tmp_decisions = self.get_nb_decisions(matches_package)
        # Fancy way to get the max of the dict, and parse it back as DecisionType
        return sd.DecisionTypes[max(tmp_decisions, key=lambda key: tmp_decisions[key])]

    def get_weighted_majority_decision(self, matches_package: Dict[str, sd.AlgoMatch]) -> sd.DecisionTypes:
        tmp_decisions = self.get_nb_decisions(matches_package, weighted=True)
        # Fancy way to get the max of the dict, and parse it back as DecisionType
        return sd.DecisionTypes[max(tmp_decisions, key=lambda key: tmp_decisions[key])]


    def get_nb_decisions(self, matches_package: Dict[str, sd.AlgoMatch], weighted=False) -> Dict:
        # Create a dict : YES=0, MAYBE=0, NO=0
        tmp_decisions = {decision.name: 0 for decision in list(sd.DecisionTypes)}

        for curr_algo in self.fe_conf.list_algos:
            self.logger.debug(f"Current algo {curr_algo}.")

            # We have a value for a computed algorithm
            curr_score = matches_package.get(curr_algo.get("algo_name"))
            if curr_score is not None:
                # We add the score of this algorithm (it's weight)
                if weighted :
                    tmp_decisions[curr_score.decision.name] += curr_algo.get("decision_weight")
                else :
                    tmp_decisions[curr_score.decision.name] += 1

        return tmp_decisions