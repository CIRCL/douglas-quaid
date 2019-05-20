#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import redis
import logging
import argparse
import pathlib
import time, datetime

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir, dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export

import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor

class Database_Requester(database_accessor.Database_Worker):
        # Heritate from the database accesso, and so has already built in access to cache, storage ..

        def __init__(self, conf: database_conf, dist_conf: distance_engine_conf):
            # STD attributes
            super().__init__(conf)

        def _to_run_forever(self):
            self.process_to_request()

        def process_to_request(self):
            # Method called infinitely, in loop

            # Trying to fetch from queue
            fetched_id, fetched_dict = self.get_from_queue(self.cache_db, self.input_queue, pickle=True)

            # If there is nothing fetched
            if not fetched_id:
                # Nothing to do
                time.sleep(0.1)
                return 0

            try:
                self.logger.info(f"DB Request worker processing {fetched_id}")
                #TODO : DO STUFF
            except:
                return 1

# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task : requesting picture to database')
    parser.add_argument("-dbc", '--configuration_file', dest="db_conf", type=dir_path, help='DB_configuration_file stored as json. Path')
    parser.add_argument("-distc", '--distance_configuration_file', dest="dist_conf", type=dir_path, help='DIST_configuration_file stored as json. Path')
    args = parser.parse_args()

    # Load the provided configuration file and create back the Configuration Object
    db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.db_conf)))
    dist_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.dist_conf)))

    # Create the Database Accessor and run it
    db_accessor = Database_Requester(db_conf, dist_conf)
    db_accessor.input_queue = "db_to_request"
    db_accessor.run(sleep_in_sec=db_conf.REQUESTER_WAIT_SEC)
