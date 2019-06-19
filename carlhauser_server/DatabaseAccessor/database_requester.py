#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor
import carlhauser_server.DatabaseAccessor.database_common as database_common
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.DatabaseAccessor.database_utilities as db_utils
import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures


class Database_Requester(database_common.Database_Common):
    # Heritate from the database accesso, and so has already built in access to cache, storage ..

    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf):
        # STD attributes
        super().__init__(db_conf, dist_conf, fe_conf)

    def process_fetched_data(self, fetched_id, fetched_dict):

        self.logger.info(f"DB Request worker processing {fetched_id}")
        self.logger.info(f"Fetched dict {fetched_dict}")

        # TODO : DO STUFF / TO REVIEW !
        # Request only : Do NOT add picture to storage

        # Get top matching clusters
        self.logger.info(f"Get top matching clusters for this picture")
        cluster_list = self.db_utils.get_cluster_list()  # DECODE
        list_clusters = self.de.get_top_matching_clusters(cluster_list, fetched_dict)  # List[scoring_datastrutures.ClusterMatch]
        list_cluster_id = [i.cluster_id for i in list_clusters]
        self.logger.info(f"Top matching clusters : {list_cluster_id}")

        # Get top matching pictures in these clusters
        self.logger.info(f"Get top matching pictures within these clusters")
        top_matching_pictures = self.de.get_top_matching_pictures_from_clusters(list_cluster_id, fetched_dict)
        self.logger.info(f"Top matching pictures : {top_matching_pictures}")

        # Depending on the quality of the match ...
        if len(top_matching_pictures) > 0 and self.de.match_enough(top_matching_pictures[0]):
            self.logger.info(f"Match is good enough with at least one cluster")
            results = scoring_datastrutures.build_response(fetched_id, list_clusters, top_matching_pictures)
            # TODO : Add to result set with "best matching picture is : #Hash from cluster #cluster_id/name ?"
        else:
            self.logger.info(f"Match not good enough, with any cluster")
            results = scoring_datastrutures.build_response(fetched_id, [], [])  # Create an answer with void lists
            # TODO : Add to result set with "Void"

        # Adding results
        self.set_request_result(self.cache_db_no_decode, fetched_id, results)

        self.logger.info(f"Request done. Results written.")


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task : requesting picture to database')
    parser.add_argument("-dbc", '--configuration_file', dest="db_conf", type=dir_path, help='DB_configuration_file stored as json. Path')
    parser.add_argument("-distc", '--distance_configuration_file', dest="dist_conf", type=dir_path, help='DIST_configuration_file stored as json. Path')
    parser.add_argument("-fec", '--feature_configuration_file', dest="fe_conf", type=dir_path, help='Feature_configuration_file stored as json. Path')
    args = parser.parse_args()

    # Load the provided configuration file and create back the Configuration Object
    db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.db_conf)))
    dist_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.dist_conf)))
    fe_conf = feature_extractor_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.fe_conf)))

    # Create the Database Accessor and run it
    db_accessor = Database_Requester(db_conf, dist_conf, fe_conf)
    db_accessor.input_queue = "db_to_request"
    db_accessor.run(sleep_in_sec=db_conf.REQUESTER_WAIT_SEC)
