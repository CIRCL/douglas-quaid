#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time
import traceback

import objsize
import redis
import pprint

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir, dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export
import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.Helpers.pickle_import_export as pickle_import_export

import carlhauser_server.Configuration.database_conf as database_conf
from carlhauser_server.Helpers.json_import_export import Custom_JSON_Encoder


class Database_Worker:

    def __init__(self, db_conf: database_conf):
        # STD attributes
        self.conf = db_conf
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Database Accessor Worker")

        # Print configuration
        json_encoder = Custom_JSON_Encoder()
        self.logger.debug(f"Configuration db_conf (db worker) : {pprint.pformat(json_encoder.encode(self.conf))}")

        # Specific
        self.input_queue = None
        self.ouput_queue = None

        # Specific attributes
        self.redis_cache = get_homedir() / self.conf.DB_DATA_PATH
        self.redis_storage = get_homedir() / self.conf.DB_DATA_PATH

        # Get sockets
        tmp_db_handler = database_start_stop.Database_StartStop(db_conf=db_conf)
        self.cache_db_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=True)
        self.cache_db_no_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=False)

        self.storage_db_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=True)
        self.storage_db_no_decode = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=False)

        # Pickler with patches
        self.pickler = pickle_import_export.Pickler()

    def add_to_queue(self, storage: redis.Redis, queue_name: str, id: str, dict_to_store: dict, pickle=False):
        """
        Push data to a specified queue, with a specific id. Wrapper to handle queuing of id(s) and separated storage of data linked to this id(s).
        Transparent way to push data to a queue
        :param storage: Redis storage to use
        :param queue_name: Target queue name
        :param id: id under which the dictionary will be stored
        :param dict_to_store: dictionary to store in the queue
        :param pickle: Do pickle the pushed data. Turn to 'False' if the data has bytes_array, even nested.
        :return: (void)
        """
        # Do stuff
        self.logger.debug(f"Worker trying to add stuff to queue={queue_name}")
        # self.logger.debug(f"Added dict: {dict_to_store}")

        try:
            # Create tmp_id for this queue
            tmp_id = '|'.join([queue_name, id])
            self.logger.debug(f"About to add id = {tmp_id}")

            # Store the dict
            self.set_dict_to_key(storage, tmp_id, dict_to_store, pickle)

            # Set an expire date
            storage.expire(tmp_id, self.conf.REQUEST_EXPIRATION)

            self.logger.debug(f"Stored= {tmp_id}")

            # Add id to the queue, to be processed
            storage.rpush(queue_name, tmp_id)  # Add the id to the queue
        except Exception as e:
            raise Exception(f"Unable to add dict and hash to {queue_name} queue : {e}")

    def get_from_queue(self, storage: redis.Redis, queue_name: str, pickle=False):
        """
        Fetch data from a specified queue. Wrapper to handle queuing of id(s) and separated storage of data linked to this id(s).
        Transparent way to pull data from a queue
        :param storage: Redis storage to use
        :param queue_name: Source queue name
        :param pickle: Do unpickle the fetched data. Turn to 'False' if the data has bytes_array, even nested.
        :return: The dict fetched from queue
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

                # TODO : Handle removal ? self.cache_db.delete(tmp_id)
                self.logger.debug(f"Stuff had been fetched from queue={queue_name}")

                return stored_id, fetched_dict
            else:
                return None, None

        except Exception as e:
            raise Exception(f"Unable to get dict and hash from {queue_name} queue : {e}")

    def get_dict_from_key(self, storage: redis.Redis, key, pickle=False):
        # Store a dict, pickled or not
        self.logger.debug(f"Fetching key : {key}")

        if pickle:
            # If correct, fetch data behind it
            pickled_object = storage.get(key)

            # Unpickling the dict
            fetched_dict = self.pickler.get_object_from_pickle(pickled_object)
        else:
            # If correct, fetch data behind it
            fetched_dict = storage.hgetall(key)

        self.logger.debug(f"Fetched dictionary : {fetched_dict.keys()}")

        return fetched_dict

    def set_dict_to_key(self, storage: redis.Redis, key, dict_to_store: dict, pickle=False, expire_time=None):
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

    def add_picture_to_storage(self, storage: redis.Redis, id, image_dict: dict):
        # Store the dictionary of hashvalues in Redis under the given id
        return self.set_dict_to_key(storage, id, image_dict, pickle=True)

    def get_picture_from_storage(self, storage: redis.Redis, id):
        return self.get_dict_from_key(storage, id, pickle=True)

    def set_request_result(self, storage: redis.Redis, id, image_dict: dict):
        # TODO : Create real request id ?

        # Create tmp_id for this queue
        tmp_id = '|'.join([id, "result"])

        return self.set_dict_to_key(storage, tmp_id, image_dict, pickle=True, expire_time=self.conf.ANSWER_EXPIRATION)

    def get_request_result(self, storage: redis.Redis, id):
        # TODO : Create real request id ?

        # Create tmp_id for this queue
        tmp_id = '|'.join([id, "result"])
        return self.get_dict_from_key(storage, tmp_id, pickle=True)

    def print_storage_view(self):
        self.logger.info("Printing REDIS Storage view")
        self.logger.info(self.storage_db_decode.keys())

    '''
    @staticmethod
    def get_unique_key(queue_name : str, id:str):
        return '|'.join([queue_name, id])
    '''

    # ==================== ------ RUNNABLE WORKER ------- ====================

    def is_halt_requested(self):
        # Check if a halt had been requested
        try:
            value = self.cache_db_decode.get("halt")
            # DEBUG # self.logger.debug(f"HALT key : {value} ")

            if not value or value == "":
                return False
            else:  # The key has been set to something, "Now","Yes", ...
                self.logger.info("HALT key detected. Worker received stop signal ... ")
                return True
        except Exception as e:
            self.logger.error(f"Impossible to know if the worker has to halt. Please review 'halt' key : {e}")
            return False

    def run(self, sleep_in_sec: int):
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
        self.logger.critical("YOU SHOULD OVERWRITE '_to_run_forever' of the database_worker class. This worker is actually doing NOTHING !")

    def long_sleep(self, sleep_in_sec: int, shutdown_check: int = 10) -> bool:
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
    parser = argparse.ArgumentParser(description='Launch a worker for a specific task.')
    parser.add_argument("-c", '--configuration_file', dest="conf", type=dir_path, help='DB_configuration_file stored as json. Path')
    args = parser.parse_args()

    # Load the provided configuration file and Create back the Configuration Object
    conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.conf)))

    # Create the Database Accessor and run it
    db_accessor = Database_Worker(conf)
    db_accessor.run(sleep_in_sec=conf.ADDER_WAIT_SEC)
