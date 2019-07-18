#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import datetime
import logging
import pprint
import sys
import time
import traceback
from typing import Dict

import objsize
import redis

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Singletons.database_start_stop as database_start_stop
import common.ImportExport.pickle_import_export as pickle_import_export
from carlhauser_server.Helpers import arg_parser
from common.ImportExport.json_import_export import Custom_JSON_Encoder
from common.environment_variable import QueueNames
from common.environment_variable import get_homedir
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class Database_Worker:

    def __init__(self, tmp_db_conf: database_conf):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Database Accessor Worker")

        # STD attributes
        self.db_conf = tmp_db_conf
        json_encoder = Custom_JSON_Encoder()

        # Print configuration
        self.logger.debug(f"Configuration db_conf (db worker) : {pprint.pformat(json_encoder.encode(self.db_conf))}")

        # Specific
        self.input_queue = None
        self.ouput_queue = None

        # Specific attributes
        self.redis_cache = get_homedir() / self.db_conf.DB_DATA_PATH
        self.redis_storage = get_homedir() / self.db_conf.DB_DATA_PATH

        # Get sockets
        tmp_db_handler = database_start_stop.Database_StartStop(db_conf=tmp_db_conf)
        self.cache_db_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=True)
        self.cache_db_no_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=False)

        self.storage_db_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=True)
        self.storage_db_no_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=False)

        # Pickler with patches
        self.pickler = pickle_import_export.Pickler()

        # Imposible to connect => Shutdown
        self.failure_nb = 0
        self.FAILURE_THRESHOLD = 10

    # ==================== ------ GET/SET QUEUE ------- ====================

    def add_to_queue(self, storage: redis.Redis, queue_name: QueueNames, input_id: str, dict_to_store: dict, pickle=False) -> bool:
        """
        Push data to a specified queue, with a specific id. Wrapper to handle queuing of id(s) and separated storage of data linked to this id(s).
        Transparent way to push data to a queue
        :param storage: Redis storage to use
        :param queue_name: Target queue name
        :param input_id: id under which the dictionary will be stored
        :param dict_to_store: dictionary to store in the queue
        :param pickle: Do pickle the pushed data. Turn to 'False' if the data has bytes_array, even nested.
        :return: (void)
        """
        # Do stuff
        self.logger.debug(f"Worker trying to add stuff to queue={queue_name}")

        try:
            # Create tmp_id for this queue
            tmp_id = '|'.join([queue_name, input_id])
            self.logger.debug(f"About to add id = {tmp_id}")

            # Store the dict
            self.set_dict_to_key(storage, tmp_id, dict_to_store, pickle)

            # Set an expire date
            storage.expire(tmp_id, self.db_conf.REQUEST_EXPIRATION)
            self.logger.debug(f"Stored= {tmp_id}")

            # Add id to the queue, to be processed
            storage.rpush(queue_name, tmp_id)  # Add the id to the queue
            return True
        except Exception as e:
            raise Exception(f"Unable to add dict and hash to {queue_name} queue : {e}")

    def get_from_queue(self, storage: redis.Redis, queue_name: QueueNames, pickle=False) -> (str, Dict):
        """
        Fetch data from a specified queue. Wrapper to handle queuing of id(s) and separated storage of data linked to this id(s).
        Transparent way to pull data from a queue
        :param storage: Redis storage to use
        :param queue_name: Source queue name
        :param pickle: Do unpickle the fetched data. Turn to 'False' if the data has bytes_array, even nested.
        :return: The fetched id of the item in the queue and the dict fetched from queue
        """
        # self.logger.debug(f"Worker trying to remove stuff from queue={queue_name}")

        try:
            # Get the next value in queue
            tmp_id = storage.lpop(queue_name)
            # self.logger.debug(f"Fetch from queue {tmp_id} of type {type(tmp_id)}")

            if tmp_id:
                self.logger.debug(f"An ID had been fetched : {tmp_id}")

                # Get the stored dict
                fetched_dict = self.get_dict_from_key(storage, tmp_id, pickle)

                # Extract info from key (Be aware that it can be bytes, and so need to be decoded)
                if type(tmp_id) is str:
                    # Already string, so no need to change anything
                    to_split = tmp_id
                else:
                    # Raw, other than string, so needs to be decoded
                    to_split = str(tmp_id.decode('utf-8'))

                stored_queue_name, stored_id = to_split.split("|")
                # TODO : Handle removal ? self.cache_db.delete(tmp_id) ==> Already expire time (24H)

                self.logger.debug(f"Stuff had been fetched from queue={queue_name}")

                return stored_id, fetched_dict
            else:
                return None, None

        except Exception as e:
            raise Exception(f"Unable to get dict and hash from {queue_name} queue : {e}")

    # ==================== ------ GET/SET DICT ------- ====================

    def set_dict_to_key(self, storage: redis.Redis, key, dict_to_store: dict, pickle=False, expire_time=None) -> bool:
        """
        Set a dict of values, pickled or not, to a key
        :param expire_time: The time after which the dict will be deleted (to prevent always-growing database), default = no expire
        :param dict_to_store: the dictionnary of values to store
        :param storage: storage to which dictionary should be stored
        :param key: The key to which the dict is linked
        :param pickle: boolean to notify if the value to store should be pickled
        :return: boolean, True if correctly stored, False if not.
        """

        # Retrieve a dict, pickled or not
        self.logger.debug(f"Setting key : {key}")

        if pickle:
            # Pickling the dict
            pickled_object = self.pickler.get_pickle_from_object(dict_to_store)
            self.logger.debug(f"Size of storage object : {objsize.get_deep_size(pickled_object)}")
            answer = storage.set(key, pickled_object)
        else:
            # Store the dict
            answer = storage.hmset(key, dict_to_store)

        if expire_time is not None:
            # Set an expire date
            storage.expire(key, expire_time)

        return answer

    def get_dict_from_key(self, storage: redis.Redis, key, pickle=False) -> Dict:
        """
        Retrieve a dict of values, pickled or not, from a key
        :param storage: storage from which dictionary should be picked
        :param key: The key to which the dict is linked
        :param pickle: boolean to notify if the value to get is pickled
        :return: The fetched dictionary (as an object)
        """

        # Store a dict, pickled or not
        self.logger.debug(f"Fetching key : {key}")

        if pickle:
            # fetch data linked to the key
            pickled_object = storage.get(key)

            # Unpickling the dict
            fetched_dict = self.pickler.get_object_from_pickle(pickled_object)
        else:
            # fetch data linked to the key
            fetched_dict = storage.hgetall(key)

        self.logger.debug(f"Fetched dictionary : {fetched_dict.keys()}")

        return fetched_dict

    # ==================== ------ GET/SET IMAGES ------- ====================

    def add_picture_to_storage(self, storage: redis.Redis, input_id: str, image_dict: dict) -> bool:
        """
        Store images as pickled dict in the provided storage
        :param storage: storage to which dictionary should be stored
        :param input_id: The key to which the picture is linked
        :param image_dict: the picture to store (as a dict)
        :return: Boolean (True = success, False = failure)
        """
        # Store the dictionary of hashvalues in Redis under the given id
        return self.set_dict_to_key(storage, input_id, image_dict, pickle=True)

    def get_picture_from_storage(self, storage: redis.Redis, input_id) -> Dict:
        """
        Retrieve images as pickled dict in the provided storage
        :param storage: storage from which picture (dict) should be stored
        :param input_id: The key to which the dict is linked
        :return: the picture (as a dict)
        """
        return self.get_dict_from_key(storage, input_id, pickle=True)

    # ==================== ------ GET/SET REQUEST ------- ====================
    def set_request_result(self, storage: redis.Redis, input_id: str, image_dict: dict) -> bool:
        """
        Store results as pickled dict in the provided storage with a configuration-defined expiration time
        :param storage: storage to which result dictionary should be stored
        :param input_id: The key to which the results is linked (modified inside)
        :param image_dict: the picture to store (as a dict)
        :return: Boolean (True = success, False = failure)
        """
        # Create tmp_id for this queue
        tmp_id = '|'.join([input_id, "result"])

        return self.set_dict_to_key(storage, tmp_id, image_dict, pickle=True, expire_time=self.db_conf.ANSWER_EXPIRATION)

    def get_request_result(self, storage: redis.Redis, input_id) -> Dict:
        """
        Retrieve results as pickled dict in the provided storage
        :param storage: storage from which results (dict) should be stored
        :param input_id: The key to which the dict is linked
        :return: the picture (as a dict)
        """
        # Create tmp_id for this queue
        tmp_id = '|'.join([input_id, "result"])
        return self.get_dict_from_key(storage, tmp_id, pickle=True)

    # ==================== ------ CHECK QUEUE EMPTINESS ------- ====================

    def are_all_queues_empty(self) -> bool:
        """
        Check if all queues (TO ADD, TO REQUEST, etc.) are empty
        :return: True if all are empty, False otherwise
        """
        if self.is_queue_empty(self.cache_db_no_decode, QueueNames.DB_TO_ADD) and \
                self.is_queue_empty(self.cache_db_no_decode, QueueNames.DB_TO_REQUEST) and \
                self.is_queue_empty(self.cache_db_no_decode, QueueNames.FEATURE_TO_ADD) and \
                self.is_queue_empty(self.cache_db_no_decode, QueueNames.FEATURE_TO_REQUEST):
            return True

        return False

    def is_queue_empty(self, storage: redis.Redis, list_name: QueueNames) -> bool:
        """
        Check if the specified Queue in the specified storage is empty
        :param storage: the storage in which the queue exist
        :param list_name: the queue name to check
        :return: True if the queue is empty, False otherwise, Exception if Queue does not exist
        """
        val = storage.llen(list_name)
        if val is None:
            raise Exception(f"Queue {list_name} is not accessible !")
        self.logger.debug(f"Length of {list_name} queue : {val}")

        return val == 0

    def print_storage_view(self):
        """
        Print all keys of the storage
        :return:
        """
        self.logger.info("Printing REDIS Storage view")
        self.logger.info(self.storage_db_decode.keys())

    # ==================== ------ RUNNABLE WORKER ------- ====================

    def is_halt_requested(self):
        """
        Check if a halt had been requested
        :return: True if halt requested (or unknown for too long), False otherwise
        """

        try:
            value = self.cache_db_decode.get("halt")
            # DEBUG # self.logger.debug(f"HALT key : {value} ")

            if not value or value == "":
                self.failure_nb = 0
                return False
            else:  # The key has been set to something, "Now","Yes", ...
                self.logger.info("HALT key detected. Worker received stop signal ... ")
                return True
        except Exception as e:
            self.logger.error(f"Impossible to know if the worker has to halt : {e}")
            self.failure_nb += 1
            if self.failure_nb > self.FAILURE_THRESHOLD:
                # There was to many failure, we stop the worker as we can't connect to DB
                self.logger.critical(f"Too many failures to connect to the DB. Stopping worker")
                return True
            return False

    def run(self, sleep_in_sec: int):
        """
        Run indefinitely except if the worker have received a stop signal.
        :param sleep_in_sec: time between two check for something to do
        :return: Nothing
        """
        try:

            self.logger.info(f'Launching {self.__class__.__name__}')
            if self.input_queue is None:
                raise Exception("No input queue set for current worker. Impossible to fetch work to do. Worker aborted.")
            if self.is_halt_requested():
                self.logger.error(f'Halt detected even before worker launch in Redis. Aborting worker launch ... ')

            while not self.is_halt_requested():
                try:
                    self._to_run_forever()
                except Exception as e:
                    self.logger.error(f'Something went terribly wrong in {self.__class__.__name__} : {e.__class__} {e}')

                if not self.long_sleep(sleep_in_sec):
                    self.logger.warning(f'Halt detected in db worker. Exiting worker execution ... ')
                    break

        except KeyboardInterrupt:
            print('Interruption detected')
            try:
                print('DB Worker stopped brutally. You should not do that :( ...')
                sys.exit(0)
            except SystemExit:
                traceback.print_exc(file=sys.stdout)

        self.logger.info(f'Shutting down {self.__class__.__name__}')

    def _to_run_forever(self):
        """
        Method called infinitely, in loop. Specified from the parent version. Fetch from database queue and call a process function on it.
        :return: Nothing
        """

        # Trying to fetch from queue (from parameters)
        fetched_id, fetched_dict = self.fetch_from_queue()

        # If there is nothing fetched
        if not fetched_id:
            # Nothing to do
            time.sleep(0.1)
        else :
            try:
                self.process_fetched_data(fetched_id, fetched_dict)

            except Exception as e:
                self.logger.error(f"Error in database worker (DB adder, db Request or FeatureExtractor or ... ) : {e}")
                self.logger.error(traceback.print_tb(e.__traceback__))

    def fetch_from_queue(self) -> (str, Dict):
        return self.get_from_queue(self.cache_db_no_decode, self.input_queue, pickle=True)

    def process_fetched_data(self, fetched_id, fetched_dict):
        """
        Method to overwrite to specify the worker. Called each time something is fetched from queue
        :param fetched_id: id to process
        :param fetched_dict: data to process
        :return: Nothing (or to be defined)
        """
        self.logger.critical("YOU SHOULD OVERWRITE 'process_fetched_data' of the database_worker class. This worker is actually doing NOTHING !")

    def long_sleep(self, sleep_in_sec: int, shutdown_check: int = 10) -> bool:
        """
        Wait a "long" time before returning, while keep checking if the worker has to stop.
        :param sleep_in_sec: time before wake-up = exit of the function
        :param shutdown_check: time between each shutdown request check.
        :return: True if no halt request had been detected, True otherwise
        """
        # Check shutdown at least as fast as sleep waiting time
        if shutdown_check > sleep_in_sec:
            shutdown_check = sleep_in_sec

        # We have the date to which we should wake up
        sleep_until = datetime.datetime.now() + datetime.timedelta(seconds=sleep_in_sec)

        # We periodically check if the worker must shutdown
        while sleep_until > datetime.datetime.now():
            time.sleep(shutdown_check)
            if self.is_halt_requested():
                return False
        return True


# Launcher for this worker. Launch this file to launch a worker
# NOTE THIS WORKER WON'T PERFORM ANY ACTION !
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task : unspecified')
    parser = arg_parser.add_arg_db_conf(parser)

    args = parser.parse_args()

    db_conf, _, _, _ = arg_parser.parse_conf_files(args)

    # Create the Database Accessor and run it
    db_accessor = Database_Worker(db_conf)
    db_accessor.run(sleep_in_sec=db_conf.ADDER_WAIT_SEC)
