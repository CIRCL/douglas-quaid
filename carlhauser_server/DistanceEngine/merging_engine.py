#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
import logging

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor

import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures


class Merging_Engine:
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Distance ORB Engine")

        # Save configuration
        self.db_conf = db_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.dist_conf = dist_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.fe_conf = fe_conf

        # TODO : Properly handle enum passed by file. Maybe https://stackoverflow.com/questions/22562425/attributeerror-cant-set-attribute-in-python ?
        self.merging_method = feature_extractor_conf.MergingMethod[self.fe_conf.merging_method]

    # ==================== ------ PICTURE-PICTURE DISTANCE ------- ====================

    def merge_algos_distance(self, distance_package: dict):
        # TODO : Complete merging / Improve
        self.logger.info(f"Received algorithms distance to merge {distance_package}")

        if self.merging_method == feature_extractor_conf.MergingMethod.MAX:
            score = self.get_max_dict(distance_package)

        elif self.merging_method == feature_extractor_conf.MergingMethod.MIN:
            score = self.get_min_dict(distance_package)

        elif self.merging_method == feature_extractor_conf.MergingMethod.MEAN:
            score = self.get_mean_dict(distance_package)

        elif self.merging_method == feature_extractor_conf.MergingMethod.WEIGHTED_MEAN:
            score = self.get_weighted_mean_dict(distance_package)

        elif self.merging_method == feature_extractor_conf.MergingMethod.HARMONIC_MEAN:
            score = self.get_harmonic_mean_dict(distance_package)

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

    # ==================== ------ COMMON ------- ====================
    @staticmethod
    def get_max_dict(distance_package: dict) -> float:
        return max(distance_package.values())

    @staticmethod
    def get_min_dict(distance_package: dict) -> float:
        return min(distance_package.values())

    @staticmethod
    def get_mean_dict(distance_package: dict) -> float:
        return sum(distance_package.values()) / len(distance_package.values())

    def get_weighted_mean_dict(self, distance_package: dict) -> float:
        sum_score = 0
        sum_weight = 0
        self.logger.debug(f"Algo list {self.fe_conf.list_algos}.")
        self.logger.debug(f"Full config {self.fe_conf}.")

        for curr_algo in self.fe_conf.list_algos:
            self.logger.debug(f"Current algo {curr_algo}.")

            # We have a value for a computed algorithm
            curr_score = distance_package.get(curr_algo.get("algo_name"))
            if curr_score is not None:
                # We add the score of this algorithm
                sum_score += curr_score
                # We add the weight of this algorithm
                sum_weight += curr_algo.get("weight")

        if sum_weight != 0:
            return sum_score / sum_weight
        else:
            raise Exception("Impossible to compute a weighted mean during algorithms outputs merging : \n"
                            "Did you put a not-null weight for activated algorithm ? Did you activated at least one algorithm ?")

    def get_harmonic_mean_dict(self, distance_package: dict) -> float:
        # TODO !
        return 0

    # TODO : 90% MAX ?
