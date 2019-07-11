#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
from common.environment_variable import dir_path
import common.ImportExport.json_import_export as json_import_export
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.DatabaseAccessor.database_common as database_common
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.static_values import QueueNames

class Database_Adder(database_common.Database_Common):
    # Heritate from the database accessor, and so has already built in access to cache, storage ..

    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf):
        # STD attributes
        super().__init__(db_conf, dist_conf, fe_conf)

    def process_fetched_data(self, fetched_id, fetched_dict):

        self.logger.info(f"DB Adder worker processing {fetched_id}")
        self.logger.info(f"Fetched dict {fetched_dict}")

        # Add picture to storage
        self.logger.info(f"Adding picture to storage under id {fetched_id}")
        self.add_picture_to_storage(self.storage_db_no_decode, fetched_id, fetched_dict)  # NOT DECODE

        # Get top matching pictures in clusters
        top_matching_pictures, list_matching_clusters = self.get_top_matching_pictures(fetched_dict)

        # Depending on the quality of the match ...
        if self.is_good_match(top_matching_pictures):
            self.logger.info(f"Match is good enough with at least one cluster")

            # Add picture to best picture's cluster
            cluster_id = top_matching_pictures[0].cluster_id
            self.db_utils.add_picture_to_cluster(fetched_id, cluster_id)

            # Re-evaluate representative picture(s) of cluster
            self.reevaluate_representative_picture_order(cluster_id, fetched_id=fetched_id)  # TODO : To defer ? No : it's not a request. No returned value. BUT TO COMPLETE !
            self.logger.info(f"Picture added in existing cluster : {cluster_id}")

        else:
            self.logger.info(f"Match not good enough, with any cluster")
            # Add picture to it's own cluster
            cluster_id = self.db_utils.add_picture_to_new_cluster(fetched_id, score=0)  # First picture is "alone" and so central
            self.logger.info(f"Picture added in its own new cluster : {cluster_id}")

        # Add to a queue, to be reviewed later, when more pictures will be added
        self.db_utils.add_to_review(fetched_id)  # TODO
        self.logger.info(f"Adding done.")

    def reevaluate_representative_picture_order(self, cluster_id, fetched_id=None):
        # Re-evaluate the representative picture of the cluster <cluster_id>,
        # knowing or not, that the last added and non evaluated picture of the cluster is <fetched_id>

        if fetched_id is None:
            # We don't know which picture was the last one added. Perform full re-evaluation
            # 0(N²) operation with N being the number of elements in the cluster

            # Get all picture ids of the cluster
            pictures_sorted_set = self.db_utils.get_pictures_of_cluster(cluster_id)

            for curr_pic in pictures_sorted_set:
                # For each picture, compute its centrality and store it
                curr_pic_dict = self.get_dict_from_key(self.storage_db_no_decode, curr_pic, pickle=True)
                centrality_score = self.compute_centrality(pictures_sorted_set, curr_pic_dict)

                # Replace the current sum (set value) of distance by the newly computed on
                self.db_utils.update_picture_score_of_cluster(cluster_id, curr_pic, centrality_score)
        else:
            # We know which picture was added last, and so begin by this one.
            # 0(2.N) operation with N being the number of elements in the cluster

            # Get all picture ids of the cluster, with their actual score
            pictures_sorted_set = self.db_utils.get_pictures_of_cluster(cluster_id, with_score=True)

            # Compute the centrality of the new picture and update its score : 0(N)
            new_pic_dict = self.get_dict_from_key(self.storage_db_no_decode, fetched_id, pickle=True)
            centrality_score = self.compute_centrality([i[0] for i in pictures_sorted_set], new_pic_dict)
            self.db_utils.update_picture_score_of_cluster(cluster_id, fetched_id, centrality_score)

            # And for each other picture, add the distance between itself and this new picture to its score : 0(N)
            for curr_pic, score in pictures_sorted_set:
                # Important ! Because current score is not updated by previous calculation (tricky race condition)
                if curr_pic == fetched_id:
                    continue
                curr_target_pic_dict = self.get_dict_from_key(self.storage_db_no_decode, curr_pic, pickle=True)
                delta_centrality, decision = self.de.get_dist_and_decision_picture_to_picture(new_pic_dict, curr_target_pic_dict)
                # Update the centrality of the current picture with the new "added value".
                self.db_utils.update_picture_score_of_cluster(cluster_id, curr_pic, score + delta_centrality)

        # TODO : Somewhat already done before. May be able to memoize the computed values ?
        return

    def compute_centrality(self, pictures_list_id: List, picture_dict) -> float:
        # Returns centrality of a picture within a list of other pictures.

        self.logger.debug(picture_dict)
        curr_sum = 0
        # For each picture, compute its distance to other picture, summing it temporary
        for curr_target_pic in pictures_list_id:
            curr_target_pic_dict = self.get_dict_from_key(self.storage_db_no_decode, curr_target_pic, pickle=True)
            dist, decision = self.de.get_dist_and_decision_picture_to_picture(picture_dict, curr_target_pic_dict)
            # TODO : use decision in centrality computation ?
            curr_sum += dist

        self.logger.debug(f"Computed centrality for {pictures_list_id}")

        return curr_sum


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task : adding picture to database')
    parser.add_argument("-dbc", '--configuration_file', dest="db_conf", type=dir_path, help='DB_configuration_file stored as json. Path')
    parser.add_argument("-distc", '--distance_configuration_file', dest="dist_conf", type=dir_path, help='DIST_configuration_file stored as json. Path')
    parser.add_argument("-fec", '--feature_configuration_file', dest="fe_conf", type=dir_path, help='Feature_configuration_file stored as json. Path')
    args = parser.parse_args()

    # Load the provided configuration file and create back the Configuration Object
    db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.db_conf)))
    dist_conf = distance_engine_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.dist_conf)))
    fe_conf = feature_extractor_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.fe_conf)))

    # Create the Database Accessor and run it
    db_accessor = Database_Adder(db_conf, dist_conf, fe_conf)
    db_accessor.input_queue = QueueNames.DB_TO_ADD
    db_accessor.run(sleep_in_sec=db_conf.ADDER_WAIT_SEC)
