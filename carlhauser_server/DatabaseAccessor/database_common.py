#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from typing import List, Dict

# ==================== ------ PERSONAL LIBRARIES ------- ====================
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_utilities as db_utils
import carlhauser_server.DatabaseAccessor.database_worker as database_accessor
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures

sys.path.append(os.path.abspath(os.path.pardir))


class Database_Common(database_accessor.Database_Worker):
    def __init__(self, tmp_db_conf: database_conf.Default_database_conf, dist_conf: distance_engine_conf.Default_distance_engine_conf, fe_conf: feature_extractor_conf.Default_feature_extractor_conf):
        # STD attributes
        super().__init__(tmp_db_conf)

        # Store configuration
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        # Distance engine
        self.de = distance_engine.Distance_Engine(self, tmp_db_conf, dist_conf, fe_conf)
        self.db_utils = db_utils.DBUtilities(db_access_decode=self.storage_db_decode, db_access_no_decode=self.storage_db_no_decode)

    # ==== COMMON ACTION OF BOTH ADDER AND REQUESTER ====

    def get_top_matching_pictures(self, fetched_dict: Dict) -> (List[scoring_datastrutures.ImageMatch], List[scoring_datastrutures.ClusterMatch]):
        """
        Extract the list of top matching pictures and the list of top matching clusters from a result dict.
        :param fetched_dict: the result (raw) dict
        :return: the List of top matching picture and the list of top matching clusters
        """

        # Get top matching clusters
        self.logger.info(f"Get top matching clusters for this picture")
        cluster_list = self.db_utils.get_cluster_list()  # DECODE

        # List[scoring_datastrutures.ClusterMatch]
        list_matching_clusters = self.de.get_top_matching_clusters(cluster_list, fetched_dict)
        list_cluster_id = [i.cluster_id for i in list_matching_clusters]
        self.logger.info(f"Top matching clusters : {list_cluster_id}")

        # Get top matching pictures in these clusters
        self.logger.info(f"Get top matching pictures within these clusters")
        top_matching_pictures = self.de.get_top_matching_pictures_from_clusters(list_cluster_id, fetched_dict)
        self.logger.info(f"Top matching pictures : {top_matching_pictures}")

        return top_matching_pictures, list_matching_clusters

    def is_good_match(self, top_matching_pictures: List[scoring_datastrutures.ImageMatch]) -> bool:
        """
        Check if a match is good enough (at least one match, not None ..)
        :param top_matching_pictures: list of top matching picture
        :return: True if correct (at least a match etc.), False otherwise
        """
        return len(top_matching_pictures) > 0 and self.de.match_enough(top_matching_pictures[0])
