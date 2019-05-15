#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import redis
import logging
import time
import argparse
import pathlib


# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir, dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export

import carlhauser_server.DatabaseAccessor.database_worker as database_accessor
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf


class Feature_Worker(database_accessor.Database_Worker):
    # Heritate from the database accesso, and so has already built in access to cache, storage ..

    def __init__(self, db_conf: database_conf, fe_conf : feature_extractor_conf):
        # STD attributes
        super().__init__(db_conf)
        self.fe_conf = fe_conf

    def _to_run_forever(self):
        self.process_to_add()

    def process_to_add(self):
            to_process_picture_id = self.cache_db.rpop("to_add") # Pop from to_add queue

            if not to_process_picture_id:
                # Nothing to do
                time.sleep(0.1)
                return 0

            try:
                self.logger.info(f"Processing {to_process_picture_id}")
                #TODO : DO STUFF

            except:
                return 1

# Launcher for this worker. Launch this file to launch a worker
# NOTE THIS WORKER WON'T PERFORM ANY ACTION !
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task.')
    parser.add_argument("-c", '--configuration_file', dest="conf_db", type=dir_path, help='DB_configuration_file stored as json. Path')
    parser.add_argument("-cfe", '--feature_conf_file', dest="conf_fe", type=dir_path, help='Feature_Extrator_configuration stored as json. Path')
    parser.add_argument("-m", '--mode', dest="mode", required=True, type=str, choices={"ADD", "REQUEST"}, help='Specify queues to work from/to for the worker.')
    # parser.add_argument("-iq", '--input_queue', dest="input_queue", type=str, help='Specify input queue')
    # parser.add_argument("-oq", '--output_queue', dest="output_queue", type=str, help='Specify output queue')

    args = parser.parse_args()

    # Load the provided configuration file and create back the configuration object
    db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.conf_db)))
    fe_conf = feature_extractor_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.conf_fe)))

    # Create the Database Accessor and run it
    feature_worker = Feature_Worker(db_conf=db_conf, fe_conf=fe_conf)
    if args.mode == "ADD" :
        feature_worker.run(sleep_in_sec=fe_conf.FEATURE_ADDER_WAIT_SEC)
    elif args.mode == "REQUEST" :
        feature_worker.run(sleep_in_sec=fe_conf.FEATURE_REQUEST_WAIT_SEC)
    else :
        print("ARG_PARSER didn't do his job : you should provide a mode for the worker, to know what to do : from where to get pictures to hash, and here to where to put the result back")


