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
        self.fe_conf = fe_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !

    # ==================== ------ PICTURE-PICTURE DISTANCE ------- ====================

    def merge_algos_distance(self, distance_package: dict):
        # TODO : Complete merging / Improve
        self.logger.info(f"Received algorithms distance to merge {distance_package}")

        return self.get_max_dict(distance_package)

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
    def get_max_dict(distance_package: dict):
        return max(distance_package.values())

    @staticmethod
    def get_mean_dict(distance_package: dict):
        return sum(distance_package.values())/len(distance_package.values())

    @staticmethod
    def get_weighted_mean_dict(distance_package: dict):
        # TODO !
        return sum(distance_package.values())/len(distance_package.values())

    # TODO : 90% MAX ?

