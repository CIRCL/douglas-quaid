#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time

import redis

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export

import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor

import carlhauser_server.DistanceEngine.cluster_engine as cluster_engine
import carlhauser_server.DistanceEngine.merging_engine as merging_engine
import carlhauser_server.DistanceEngine.distance_engine as distance_engine


class Database_Adder(database_accessor.Database_Worker):
    # Heritate from the database accessor, and so has already built in access to cache, storage ..

    def __init__(self, db_conf: database_conf, dist_conf: distance_engine_conf):
        # STD attributes
        super().__init__(db_conf)

        # Get sockets
        tmp_db_handler = database_start_stop.Database_StartStop(conf=db_conf)

        # reconnect to storages, without decoding
        self.storage_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=False)
        self.cache_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=False)

        # Distance engine
        self.de = distance_engine.Distance_Engine(db_conf, dist_conf)
        self.me = merging_engine.Merging_Engine(db_conf, dist_conf)
        self.ce = cluster_engine.Cluster_Engine(db_conf, dist_conf)

    def _to_run_forever(self):
        self.process_to_add()

    def process_to_add(self):
        # Method called infinitely, in loop

        # Trying to fetch from queue (to_add)
        fetched_id, fetched_dict = self.get_from_queue(self.cache_db, self.input_queue, pickle=True)

        # If there is nothing fetched
        if not fetched_id:
            # Nothing to do
            time.sleep(0.1)
            return 0

        try:
            self.logger.info(f"DB Adder worker processing {fetched_id}")
            self.logger.info(f"Fetched dict {fetched_dict}")

            # Add picture to storage
            self.logger.info(f"Adding picture to storage under id {fetched_id}")
            self.ce.add_picture_to_storage(fetched_id, fetched_dict)

            # Get top matching clusters
            self.logger.info(f"Getting top matching clusters for this picture")
            list_clusters = self.ce.get_top_matching_clusters(fetched_dict)

            # Get top matching pictures in these clusters
            self.logger.info(f"Getting top matching pictures within these clusters")
            top_matching_pictures = self.ce.get_top_matching_pictures_from_clusters(list_clusters, fetched_dict)

            # Depending on the quality of the match ...
            if self.ce.match_enough(top_matching_pictures[0][0]):
                # Add picture to best picture's cluster
                # TODO : NOPE = TOO COMPLEX FOR REVERSE LOOKUP. JUST STORED IN PREVIOUS RESULT cluster_id = self.ce.get_cluster(top_matching_pictures[0])
                cluster_id = top_matching_pictures[0][1]
                self.ce.add_picture_to_cluster(fetched_id, cluster_id)
                # TODO : To defer ?
                # Re-evaluate representative picture(s) of cluster
                self.ce.reevaluate_representative_picture_order(fetched_id, cluster_id)
                self.logger.info(f"Picture added in existing cluster : {cluster_id}")

            else:
                # Add picture to it's own cluster
                cluster_id = self.ce.add_picture_to_new_cluster(fetched_id)
                self.logger.info(f"Picture added in its own new cluster : {cluster_id}")

            # Add to a queue, to be reviewed later, when more pictures will be added
            self.ce.add_to_review(fetched_id)

        except Exception as e:
            self.logger.error(f"Error during picture adding {e}")
        return 1

# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task : adding picture to database')
    parser.add_argument("-dbc", '--configuration_file', dest="db_conf", type=dir_path, help='DB_configuration_file stored as json. Path')
    parser.add_argument("-distc", '--distance_configuration_file', dest="dist_conf", type=dir_path, help='DIST_configuration_file stored as json. Path')
    args = parser.parse_args()

    # Load the provided configuration file and create back the Configuration Object
    db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.db_conf)))
    dist_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.dist_conf)))

    # Create the Database Accessor and run it
    db_accessor = Database_Adder(db_conf, dist_conf)
    db_accessor.input_queue = "db_to_add"
    db_accessor.run(sleep_in_sec=db_conf.ADDER_WAIT_SEC)
