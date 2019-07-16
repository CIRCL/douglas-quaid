#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
from typing import Dict

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_worker as database_accessor
import carlhauser_server.FeatureExtractor.picture_hasher as picture_hasher
import carlhauser_server.FeatureExtractor.picture_orber as picture_orber
from carlhauser_server.Helpers import arg_parser
from common.environment_variable import load_server_logging_conf_file, make_small_line, QueueNames

load_server_logging_conf_file()


class Feature_Worker(database_accessor.Database_Worker):
    """
    Heritate from the database accessor, and so has already built in access to cache, storage ..
    """

    def __init__(self, tmp_db_conf: database_conf, tmp_fe_conf: feature_extractor_conf):
        # STD attributes
        super().__init__(tmp_db_conf)

        self.fe_conf = tmp_fe_conf

        self.picture_hasher = picture_hasher.Picture_Hasher(tmp_fe_conf)
        self.picture_orber = picture_orber.Picture_Orber(tmp_fe_conf)

    def fetch_from_queue(self) -> (str, Dict):
        """
        Overwriting the existing fetching function, to prevent PICKLING when fetching
        :return: A string representing the id of the new fetched data, and the fetched associated dict
        """
        return self.get_from_queue(self.cache_db_no_decode, self.input_queue)

    def process_fetched_data(self, fetched_id, fetched_dict):
        """
        From a fetch id and a fetch asssociated dict, compute the hashes
        and orbing of current picture and add it to next queue
        :param fetched_id: id to process
        :param fetched_dict: data to process
        :return: Nothing (or to be defined)
        """
        # Get picture from picture_id
        picture = fetched_dict[b"img"]
        self.logger.info(f"Loaded picture {type(picture)}")

        # Get hash values of picture
        hash_dict = self.picture_hasher.hash_picture(picture)
        self.logger.debug(f"Computed hashes : {hash_dict}")

        # Get ORB values of picture
        orb_dict = self.picture_orber.orb_picture(picture)
        self.logger.debug(f"Computed orb values : {orb_dict}")

        # Merge dictionaries
        merged_dict = {**hash_dict, **orb_dict}
        self.logger.debug(f"To send to db dict : {merged_dict}")

        # Remove old data and send dictionary in hashmap to redis
        # TODO : self.cache_db.del(fetched_id) # There is already an expire time
        self.add_to_queue(self.cache_db_no_decode, self.ouput_queue, fetched_id, merged_dict, pickle=True)
        print(make_small_line())
        print("Feature Worker ready to accept more queries.")

# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task.')

    parser = arg_parser.add_arg_db_conf(parser)
    parser = arg_parser.add_arg_fe_conf(parser)
    parser = arg_parser.add_mode(parser)

    args = parser.parse_args()

    db_conf, dist_conf, fe_conf, ws_conf = arg_parser.parse_conf_files(args)

    # Create the Feature Worker and run it
    feature_worker = Feature_Worker(tmp_db_conf=db_conf, tmp_fe_conf=fe_conf)
    if args.mode == "ADD":
        feature_worker.input_queue = QueueNames.FEATURE_TO_ADD
        feature_worker.ouput_queue = QueueNames.DB_TO_ADD
        feature_worker.run(sleep_in_sec=fe_conf.FEATURE_ADDER_WAIT_SEC)
    elif args.mode == "REQUEST":
        feature_worker.input_queue = QueueNames.FEATURE_TO_REQUEST
        feature_worker.ouput_queue = QueueNames.DB_TO_REQUEST
        feature_worker.run(sleep_in_sec=fe_conf.FEATURE_REQUEST_WAIT_SEC)
    else:
        print("ARG_PARSER didn't do his job : you should provide a mode for the worker, to know what to do : from where to get pictures to hash, and here to where to put the result back")
