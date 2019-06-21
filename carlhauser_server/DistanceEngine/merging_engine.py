#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from typing import Dict, List

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

    def merge_algos_distance(self, matches_package: Dict[str, sd.AlgoMatch]) -> float:
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

    def merge_algos_decision(self, matches_package: Dict[str, sd.AlgoMatch]) -> sd.DecisionTypes:
        # TODO : Complete merging / Improve
        self.logger.info(f"Received algorithms distance to merge {matches_package}")

        if self.decision_merging_method == feature_extractor_conf.Decision_MergingMethod.PARETO:
            score = self.get_pareto_decision(matches_package)

        elif self.decision_merging_method == feature_extractor_conf.Decision_MergingMethod.MAJORITY:
            score = self.get_majority_decision(matches_package)

        elif self.decision_merging_method == feature_extractor_conf.Decision_MergingMethod.WEIGHTED_MAJORITY:
            score = self.get_weighted_majority_decision(matches_package)

        elif self.decision_merging_method == feature_extractor_conf.Decision_MergingMethod.PYRAMID:
            score = self.get_pyramid_decision(matches_package)

        else:
            raise Exception("Unrecognized merging method to merge algorithm output into one value. Please review configuration file.")

        return score

    # ==================== ------ PICTURE-CLUSTER DISTANCE ------- ====================

    def merge_pictures_distance(self, distance_list: List[float]) -> float:
        # TODO : Complete merging / Improve
        self.logger.info(f"Received picture-cluster's picture distance to merge {distance_list}")
        if len(distance_list) != 0:
            return max(distance_list)
        else:
            self.logger.error(f"A Cluster is empty but exists. Structural behavior error detected.")
            raise Exception("Empty cluster, but exists.")
            return None

    def merge_pictures_decisions(self, decision_list: List[sd.DecisionTypes]) -> sd.DecisionTypes:
        # TODO : Complete merging / Improve
        self.logger.info(f"Received picture-cluster's picture decision to merge {decision_list}")
        if len(decision_list) != 0:
            # Cosntruct a dict : YES=0, MAYBE=0, NO=0
            tmp_decisions = {decision.name: 0 for decision in list(sd.DecisionTypes)}
            # Iterate to count decision
            for curr_decision in decision_list :
                tmp_decisions[curr_decision.name] += 1

            return self.get_prevalent_decision(tmp_decisions)
        else:
            self.logger.error(f"A Cluster is empty but exists. Structural behavior error detected.")
            raise Exception("Empty cluster, but exists.")
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
            # self.logger.debug(f"Current algo {curr_algo}.")

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
        for curr_decision in sd.DecisionTypes:
            if tmp_decisions[curr_decision.name] > 0.8 * nb_decisions:
                return curr_decision
        # else, return maybe
        return sd.DecisionTypes.MAYBE

    def get_majority_decision(self, matches_package: Dict[str, sd.AlgoMatch]) -> sd.DecisionTypes:
        tmp_decisions = self.get_nb_decisions(matches_package)
        # Fancy way to get the max of the dict, and parse it back as DecisionType
        # return sd.DecisionTypes[max(tmp_decisions, key=lambda key: tmp_decisions[key])]
        return self.get_prevalent_decision(tmp_decisions)

    def get_weighted_majority_decision(self, matches_package: Dict[str, sd.AlgoMatch]) -> sd.DecisionTypes:
        tmp_decisions = self.get_nb_decisions(matches_package, weighted=True)
        # Fancy way to get the max of the dict, and parse it back as DecisionType
        # return sd.DecisionTypes[max(tmp_decisions, key=lambda key: tmp_decisions[key])]
        return self.get_prevalent_decision(tmp_decisions)

    def get_prevalent_decision(self, decision_counter: Dict[sd.DecisionTypes, int]) -> sd.DecisionTypes:
        return sd.DecisionTypes[max(decision_counter, key=lambda key: decision_counter[key])]

    def get_pyramid_decision(self, matches_package: Dict[str, sd.AlgoMatch]) -> sd.DecisionTypes:
        weight_to_algo = {}
        algo_list = []

        # Get algo computed among all available algorithms
        for curr_algo in self.fe_conf.list_algos:
            if matches_package.get(curr_algo.get("algo_name")) is not None:
                algo_list.append(curr_algo)

        # Create lists in dict as <weights => []>
        for curr_algo in algo_list:
            weight_to_algo[curr_algo.get("decision_weight")] = []

        # Create dict <weights => [algo1, algo2, ..]>
        for curr_algo in algo_list:
            weight_to_algo[curr_algo.get("decision_weight")].append(curr_algo)

        # We begin with "higher weight" algorithms and go on
        for key in sorted(weight_to_algo, reverse=True):
            # We get the list of algorithm at this "weight level"
            tmp_list_algo = weight_to_algo[key]

            # We group all matches results, related to these algorithms
            tmp_list_matches = {}
            for algo in tmp_list_algo:
                tmp_list_matches[algo.get("algo_name")] = matches_package.get(algo.get("algo_name"))

            # We take a decision up to all algorithms at this weight level
            decision = self.get_majority_decision(tmp_list_matches)

            # If the decision is YES or NO, we stop here
            if decision != sd.DecisionTypes.MAYBE:
                return decision
            # Else, we continue for the "next lower level of algorithms" in next iteration

        # If we went through all algorithms, and none were giving the same "result". We send back "MAYBE"
        return sd.DecisionTypes.MAYBE

    def get_nb_decisions(self, matches_package: Dict[str, sd.AlgoMatch], weighted=False) -> Dict:
        # Create a dict : YES=0, MAYBE=0, NO=0
        tmp_decisions = {decision.name: 0 for decision in list(sd.DecisionTypes)}

        for curr_algo in self.fe_conf.list_algos:
            # self.logger.debug(f"Current algo {curr_algo}.")

            # We have a value for a computed algorithm
            curr_score = matches_package.get(curr_algo.get("algo_name"))
            if curr_score is not None:
                # We add the score of this algorithm (it's weight)
                if weighted:
                    tmp_decisions[curr_score.decision.name] += curr_algo.get("decision_weight")
                else:
                    tmp_decisions[curr_score.decision.name] += 1

        return tmp_decisions
