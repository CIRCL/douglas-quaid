#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================

import argparse
import os
import sys


# ==================== ------ PERSONAL LIBRARIES ------- ====================

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_common as database_common
import carlhauser_server.DistanceEngine.scoring_datastrutures as score_datastruct
from carlhauser_server.Helpers import arg_parser
from common.environment_variable import QueueNames

sys.path.append(os.path.abspath(os.path.pardir))


class Database_Requester(database_common.Database_Common):
    """
    Heritate from the database common, and so has already built in access to cache, storage ..
    """

    def __init__(self, tmp_db_conf: database_conf.Default_database_conf,
                 tmp_dist_conf: distance_engine_conf.Default_distance_engine_conf,
                 tmp_fe_conf: feature_extractor_conf.Default_feature_extractor_conf):
        # STD attributes
        super().__init__(tmp_db_conf, tmp_dist_conf, tmp_fe_conf)

    def process_fetched_data(self, fetched_id, fetched_dict):
        """
        Method to overwrite to specify the worker. Called each time something is fetched from queue.
        Perform calculation on the database to fetch near pictures. Does not add the requested picture to the database
        :param fetched_id: id to process
        :param fetched_dict: data to process
        :return: Nothing (or to be defined)
        """
        self.logger.info(f"DB Request worker processing {fetched_id}")
        self.logger.info(f"Fetched dict {fetched_dict}")

        # Beaware, that this is a request only : Do NOT add picture to storage

        # Get top matching pictures in clusters
        top_matching_pictures, list_matching_clusters = self.get_top_matching_pictures(fetched_dict)

        # Depending on the quality of the match ...
        if self.is_good_match(top_matching_pictures):
            self.logger.info(f"Match is good enough with at least one cluster")
            results = score_datastruct.build_response(fetched_id, list_matching_clusters, top_matching_pictures)
        else:
            # Create an answer with void lists
            self.logger.info(f"Match not good enough, with any cluster")
            results = score_datastruct.build_response(fetched_id, [], [])

        # Adding results
        self.set_request_result(self.cache_db_no_decode, fetched_id, results)

        self.logger.info(f"Request done. Results written.")


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task : requesting picture to database')
    parser = arg_parser.add_arg_db_conf(parser)
    parser = arg_parser.add_arg_dist_conf(parser)
    parser = arg_parser.add_arg_fe_conf(parser)

    args = parser.parse_args()

    db_conf, dist_conf, fe_conf, _ = arg_parser.parse_conf_files(args)

    # Create the Database Accessor and run it
    db_accessor = Database_Requester(db_conf, dist_conf, fe_conf)
    db_accessor.input_queue = QueueNames.DB_TO_REQUEST
    db_accessor.run(sleep_in_sec=db_conf.REQUESTER_WAIT_SEC)
