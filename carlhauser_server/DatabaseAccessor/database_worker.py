#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import redis
import logging
import argparse
import pathlib
import time, datetime
import objsize

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir, dir_path
import carlhauser_server.Helpers.json_import_export as json_import_export
import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.Helpers.pickle_import_export as pickle_import_export

import carlhauser_server.Configuration.database_conf as database_conf


class Database_Worker():

    def __init__(self, conf: database_conf):
        # STD attributes
        self.conf = conf
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Database Accessor Worker")

        # Specific
        self.input_queue = None
        self.ouput_queue = None

        # Specific attributes
        self.redis_cache = get_homedir() / self.conf.DB_DATA_PATH
        self.redis_storage = get_homedir() / self.conf.DB_DATA_PATH

        # Get sockets
        tmp_db_handler = database_start_stop.Database_StartStop(conf=conf)
        self.storage_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=True)  #
        self.cache_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=True)

        # Pickler with patches
        self.pickler = pickle_import_export.Pickler()
        # self.key_prefix = 'caida'
        # self.storage_root = storage_directory / 'caida'
        # self.storagedb.sadd('prefixes', self.key_prefix)

    '''
    
    def add_to_queue(self, storage: redis.Redis, queue_name: str, id: str, dict_to_store: dict):
        # Do stuff
        self.logger.debug(f"Worker trying to add stuff to queue={queue_name}")
        # self.logger.debug(f"Added dict: {dict_to_store}")

        try:
            # Create tmp_id for this queue
            tmp_id = '|'.join([queue_name, id])
            self.logger.debug(f"About to add id = {tmp_id}")

            # Store the dict and set an expire date
            storage.hmset(tmp_id, dict_to_store)
            storage.expire(tmp_id, self.conf.REQUEST_EXPIRATION)

            self.logger.debug(f"Stored= {tmp_id}")

            # Add id to the queue, to be processed
            storage.rpush(queue_name, tmp_id)  # Add the id to the queue
        except Exception as e:
            raise Exception(f"Unable to add dict and hash to {queue_name} queue : {e}")

    def get_from_queue(self, storage: redis.Redis, queue_name: str):
        # self.logger.debug(f"Worker trying to remove stuff from queue={queue_name}")

        try:
            # Get the next value in queue
            tmp_id = storage.lpop(queue_name)

            if tmp_id:
                self.logger.debug(f"An ID has been fetched : {tmp_id}")

                # If correct, fetch data behind it
                fetched_dict = storage.hgetall(tmp_id)

                self.logger.debug(f"Fetched dictionnary : {fetched_dict.keys()}")

                stored_queue_name, stored_id = str(tmp_id).split("|")
                # TODO : Handle removal ? self.cache_db.delete(tmp_id)
                self.logger.debug(f"Stuff had been fetched from queue={queue_name}")

                return stored_id, fetched_dict
            else:
                return None, None

        except Exception as e:
            raise Exception(f"Unable to get dict and hash from {queue_name} queue : {e}")

    
    
    '''

    def add_to_queue(self, storage: redis.Redis, queue_name: str, id: str, dict_to_store: dict, pickle=False):
        '''
        Push data to a specified queue, with a specific id. Wrapper to handle queuing of id(s) and separated storage of data linked to this id(s).
        Transparent way to push data to a queue
        :param storage: Redis storage to use
        :param queue_name: Target queue name
        :param id: id under which the dictionary will be stored
        :param dict_to_store: dictionary to store in the queue
        :param pickle: Do pickle the pushed data. Turn to 'False' if the data has bytes_array, even nested.
        :return: (void)
        '''
        # Do stuff
        self.logger.debug(f"Worker trying to add stuff to queue={queue_name}")
        # self.logger.debug(f"Added dict: {dict_to_store}")

        try:
            # Create tmp_id for this queue
            tmp_id = '|'.join([queue_name, id])
            self.logger.debug(f"About to add id = {tmp_id}")

            if pickle :
                # Pickling the dict
                pickled_object = self.pickler.get_pickle_from_object(dict_to_store)
                self.logger.debug(f"Size of storage object : {objsize.get_deep_size(pickled_object)}")
                storage.set(tmp_id, pickled_object)
            else :
                # Store the dict
                storage.hmset(tmp_id, dict_to_store)

            # Set an expire date
            storage.expire(tmp_id, self.conf.REQUEST_EXPIRATION)

            self.logger.debug(f"Stored= {tmp_id}")

            # Add id to the queue, to be processed
            storage.rpush(queue_name, tmp_id)  # Add the id to the queue
        except Exception as e:
            raise Exception(f"Unable to add dict and hash to {queue_name} queue : {e}")

    def get_from_queue(self, storage: redis.Redis, queue_name: str, pickle=False):
        '''
        Fetch data from a specified queue. Wrapper to handle queuing of id(s) and separated storage of data linked to this id(s).
        Transparent way to pull data from a queue
        :param storage: Redis storage to use
        :param queue_name: Source queue name
        :param pickle: Do unpickle the fetched data. Turn to 'False' if the data has bytes_array, even nested.
        :return: The dict fetched from queue
        '''
        # self.logger.debug(f"Worker trying to remove stuff from queue={queue_name}")

        try:
            # Get the next value in queue
            tmp_id = storage.lpop(queue_name)

            if tmp_id:
                self.logger.debug(f"An ID has been fetched : {tmp_id}")

                if pickle:
                    # If correct, fetch data behind it
                    pickled_object = storage.get(tmp_id)

                    # Unpickling the dict
                    fetched_dict = self.pickler.get_object_from_pickle(pickled_object)
                else:
                    # If correct, fetch data behind it
                    fetched_dict = storage.hgetall(tmp_id)

                self.logger.debug(f"Fetched dictionary : {fetched_dict.keys()}")

                stored_queue_name, stored_id = str(tmp_id).split("|")
                # TODO : Handle removal ? self.cache_db.delete(tmp_id)
                self.logger.debug(f"Stuff had been fetched from queue={queue_name}")

                return stored_id, fetched_dict
            else:
                return None, None

        except Exception as e:
            raise Exception(f"Unable to get dict and hash from {queue_name} queue : {e}")

    '''
    @staticmethod
    def get_unique_key(queue_name : str, id:str):
        return '|'.join([queue_name, id])
    '''

    # ==================== ------ RUNNABLE WORKER ------- ====================

    def is_halt_requested(self):
        # Check if a halt had been requested
        try:
            value = self.cache_db.get("halt")
            if not value:
                return False
            else:  # The key has been set to something, "Now","Yes", ...
                return True
        except:
            self.logger.error("Impossible to know if the worker has to halt. Please review 'halt' key")

    def run(self, sleep_in_sec: int):
        self.logger.info(f'Launching {self.__class__.__name__}')
        if self.input_queue is None:
            raise Exception("No input queue set for current worker. Impossible to fetch work to do. Worker aborted.")
        while not self.is_halt_requested():
            try:
                self._to_run_forever()
            except Exception as e:
                self.logger.exception(f'Something went terribly wrong in {self.__class__.__name__} : {e}')

            if not self.long_sleep(sleep_in_sec):
                break

        self.logger.info(f'Shutting down {self.__class__.__name__}')

    def _to_run_forever(self):
        self.logger.critical("YOU SHOULD OVERWRITE '_to_run_forever' of the database_worker class. This worker is actually doing NOTHING !")
        pass

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
