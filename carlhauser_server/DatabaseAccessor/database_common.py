#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
import time
import traceback

# ==================== ------ PERSONAL LIBRARIES ------- ====================
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_utilities as db_utils
import carlhauser_server.DatabaseAccessor.database_worker as database_accessor
import carlhauser_server.DistanceEngine.distance_engine as distance_engine

sys.path.append(os.path.abspath(os.path.pardir))

class Database_Common(database_accessor.Database_Worker):
    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf):
        # STD attributes
        super().__init__(db_conf)

        # Store configuration
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        # Distance engine
        self.de = distance_engine.Distance_Engine(self, db_conf, dist_conf, fe_conf)
        self.db_utils = db_utils.DBUtilities(db_access_decode=self.storage_db_decode, db_access_no_decode=self.storage_db_no_decode)

    def _to_run_forever(self):
        # Method called infinitely, in loop

        # Trying to fetch from queue (to_add)
        fetched_id, fetched_dict = self.get_from_queue(self.cache_db_no_decode, self.input_queue, pickle=True)

        # If there is nothing fetched
        if not fetched_id:
            # Nothing to do
            time.sleep(0.1)
            return 0

        try:
            self.process_fetched_data(fetched_id, fetched_dict)

        except Exception as e:
            self.logger.error(f"Error in database accessors : {e}")
            self.logger.error(traceback.print_tb(e.__traceback__))

        return 1

    def process_fetched_data(self, fetched_id, fetched_dict):
        self.logger.error(f"'process_fetched_data' must be overwritten ! No action performed by this worker.")

    # ==== COMMON ACTION OF BOTH ADDER AND REQUESTER ====

    def get_top_matching_pictures(self, fetched_dict):
        # Get top matching clusters
        self.logger.info(f"Get top matching clusters for this picture")
        cluster_list = self.db_utils.get_cluster_list()  # DECODE
        list_matching_clusters = self.de.get_top_matching_clusters(cluster_list, fetched_dict)  # List[scoring_datastrutures.ClusterMatch]
        list_cluster_id = [i.cluster_id for i in list_matching_clusters]
        self.logger.info(f"Top matching clusters : {list_cluster_id}")

        # Get top matching pictures in these clusters
        self.logger.info(f"Get top matching pictures within these clusters")
        top_matching_pictures = self.de.get_top_matching_pictures_from_clusters(list_cluster_id, fetched_dict)
        self.logger.info(f"Top matching pictures : {top_matching_pictures}")

        return top_matching_pictures, list_matching_clusters

    def is_good_match(self, top_matching_pictures):
        return len(top_matching_pictures) > 0 and self.de.match_enough(top_matching_pictures[0])
