#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_worker
import carlhauser_server.DistanceEngine.distance_hash as distance_hash
import carlhauser_server.DistanceEngine.distance_orb as distance_orb
import carlhauser_server.DistanceEngine.merging_engine as merging_engine

import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures


class Distance_Engine:
    def __init__(self, parent: database_worker, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("... which is a Distance Engine")

        # Save configuration
        self.db_conf = db_conf
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        # Reference to database worker parent to get accessors
        self.parent = parent

        # Create distance extractor
        self.distance_hash = distance_hash.Distance_Hash(db_conf, dist_conf, fe_conf)
        self.distance_orb = distance_orb.Distance_ORB(db_conf, dist_conf, fe_conf)
        self.merging_engine = merging_engine.Merging_Engine(db_conf, dist_conf, fe_conf)

    # ==================== ------ INTER ALGO DISTANCE ------- ====================
    def get_distance_algos_to_algos(self, pic_package_from, pic_package_to):
        # Compute a list of distance from two image representation

        # Get hash distances
        hash_dict = self.distance_hash.hash_distance(pic_package_from, pic_package_to)
        self.logger.debug(f"Computed hashes distance : {hash_dict}")

        # Get ORB distances
        orb_dict = self.distance_orb.orb_distance(pic_package_from, pic_package_to)
        self.logger.debug(f"Computed orb distance : {orb_dict}")

        # Merge distances dictionaries
        merged_dict = {**hash_dict, **orb_dict}
        self.logger.debug(f"Distance dict : {merged_dict}")

        return merged_dict

    # ==================== ------ INTER IMAGE DISTANCE ------- ====================
    def get_distance_picture_to_picture(self, pic_package_from, pic_package_to):
        # From distance between algos, obtain the distance between pictures
        merged_dict = self.get_distance_algos_to_algos(pic_package_from, pic_package_to)
        return self.merging_engine.merge_algos_distance(merged_dict)

    def match_enough(self, matching_picture: scoring_datastrutures.ImageMatch) -> bool:
        # Check if the matching pictures provided are "close enough" of the current picture.

        # Check if the picture is too far or not
        if matching_picture.distance <= self.dist_conf.MAX_DIST_FOR_NEW_CLUSTER:
            return True

        # Picture is too "far"
        return False

    # ==================== ------ PICTURE TO CLUSTER DISTANCE ------- ====================

    def get_top_matching_clusters(self, cluster_list: list, image_dict: dict) -> List[scoring_datastrutures.ClusterMatch]:
        # Evaluate the similarity between the given picture and each cluster's representative picture
        # Returns a list of the N closest clusters
        self.logger.debug(f"Finding top matching clusters for current picture in cluster list {cluster_list}")

        TOP_N_CLUSTERS = self.dist_conf.TOP_N_CLUSTERS
        top_n_storage = scoring_datastrutures.TopN(TOP_N_CLUSTERS)

        # Evaluate similarity to each cluster
        for curr_cluster in cluster_list:
            self.logger.debug(f"Evaluating distance from current picture to cluster #{curr_cluster}")

            # Evaluate current distance to cluster
            tmp_dist = self.get_distance_picture_to_cluster(curr_cluster, image_dict)

            # Store in datastructure
            tmp_cluster_match = scoring_datastrutures.ClusterMatch(cluster_id=curr_cluster, distance=tmp_dist)
            top_n_storage.add_element(tmp_cluster_match)

        # get top N clusters = Ask datastructure to return its top list
        return top_n_storage.get_top_n()

    def get_distance_picture_to_cluster(self, cluster_id, image_dict: dict):
        # Go through N first picture of given cluster, and test their distance to given image
        # Merge the result into one unified distance
        self.logger.debug(f"Computing distance between cluster {cluster_id} and current picture")

        PICT_TO_TEST_PER_CLUSTER = self.dist_conf.PICT_TO_TEST_PER_CLUSTER

        list_dist = []
        curr_picture_sorted_set = self.parent.db_utils.get_pictures_of_cluster(cluster_id)  # DECODE

        self.logger.debug(f"Retrieved pictures of cluster #{cluster_id} are {curr_picture_sorted_set}")

        for i, curr_picture in enumerate(curr_picture_sorted_set):
            if i < PICT_TO_TEST_PER_CLUSTER:
                self.logger.debug(f"Evaluating picture #{i} of current cluster")
                # We still have pictures to test for this cluster
                # Get picture dict
                curr_pic_dict = self.parent.get_dict_from_key(self.parent.storage_db_no_decode, curr_picture, pickle=True)

                # Evaluate distance between actual picture and cluster's pictures
                list_dist.append(self.get_distance_picture_to_picture(curr_pic_dict, image_dict))
            else:
                # We have tested the N first pictures of the cluster and so stop here
                break

        # Evaluation of the distance between pictures
        return self.merging_engine.merge_pictures_distance(list_dist)

    # ==================== ------ PICTURE TO ALL PICTURES DISTANCE ------- ====================

    def get_top_matching_pictures_from_clusters(self, cluster_list: list, image_dict: dict) -> List[scoring_datastrutures.ImageMatch]:
        # Evaluate the similarity between the given picture and all pictures of cluster list.
        # Returns a list of the N closest pictures and cluster, with distance

        self.logger.debug(f"Finding top matching pictures for current picture in all pictures of all clusters of the list={cluster_list}")

        # TODO : 1 only ? We want to connect only to one picture the current picture ?
        TOP_N_PICTURES = self.dist_conf.TOP_N_PICTURES
        top_n_storage = scoring_datastrutures.TopN(TOP_N_PICTURES)

        # For each cluster, iterate over all pictures of this cluster
        for curr_cluster in cluster_list:
            curr_picture_set = self.parent.db_utils.get_pictures_of_cluster(curr_cluster)

            for curr_picture in curr_picture_set:
                # Get picture dict
                curr_pic_dict = self.parent.get_dict_from_key(self.parent.storage_db_no_decode, curr_picture, pickle=True)

                # Evaluate distance between actual picture and cluster's pictures
                tmp_dist = self.get_distance_picture_to_picture(curr_pic_dict, image_dict)

                # Keep only N best picture = Store in datastructure
                tmp_image_match = scoring_datastrutures.ImageMatch(image_id=curr_picture, cluster_id=curr_cluster, distance=tmp_dist)
                top_n_storage.add_element(tmp_image_match)

        # get top N pictures
        return top_n_storage.get_top_n()

    # ==================== ------ PICTURE TO ALL PICTURES DISTANCE ------- ====================

    def get_best_n_pictures_of_cluster(self, cluster_id):
        # Get N best pictures of the given cluster
        # TODO : To complete with ZSET ...
        return
