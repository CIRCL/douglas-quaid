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


class Database_Worker():

    def __init__(self, conf: database_conf):
        # STD attributes
        self.conf = conf
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Database Accessor Worker")

        # Specific attributes
        self.redis_cache = get_homedir() / self.conf.DB_DATA_PATH
        self.redis_storage = get_homedir() / self.conf.DB_DATA_PATH

        # Get sockets
        tmp_db_handler = database_start_stop.Database_StartStop(conf=conf)
        self.storage_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=True)
        self.cache_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=True)

        # self.key_prefix = 'caida'
        # self.storage_root = storage_directory / 'caida'
        # self.storagedb.sadd('prefixes', self.key_prefix)

    def add_to_queue(self, queue_name, id, data):
        # Do stuff
        print(f"I'm adding stuff to the queue : {self.cache_db}")

        # im.save(output, format=im.format)
        print("Added data: ", data)

        '''
        data = {
          'seller_id': seller,
          'item_id': item,
          'price': price,
          'buyer_id': buyer,
          'time': time.time()        
           }
        
        '''

        try:
            self.cache_db.set(name=id + "|picture", value=data, ex=self.conf.REQUEST_EXPIRATION)  # 1 day expiration for data
            self.cache_db.rpush(queue_name, id)  # Add the id to the queue
        except:
            raise Exception("Unable to add picture and hash to 'to_add' queue.")

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
