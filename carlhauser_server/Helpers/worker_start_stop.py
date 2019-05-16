#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import subprocess
import pathlib
import time
import redis
import logging
import datetime

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.template_singleton import Singleton
from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Helpers.json_import_export as json_import_export
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Helpers.database_start_stop as database_start_stop


# ==================== ------ PATHS ------- ====================

class Worker_StartStop(object, metaclass=Singleton):
    # Singleton class that handle database access
    _instance = None

    def __init__(self, conf: database_conf):
        # STD attributes
        self.conf = conf
        self.logger = logging.getLogger(__name__)

        # Specific attributes
        # self.worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'DatabaseAccessor', 'datanase_worker.py')
        self.adder_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'DatabaseAccessor', 'database_adder.py')
        self.requester_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'DatabaseAccessor', 'database_requester.py')

        self.feature_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'FeatureExtractor', 'feature_worker.py')

        # Worker lists
        # self.worker_list = []
        self.adder_worker_list = []
        self.requester_worker_list = []
        self.feature_adder_worker_list = []
        self.feature_requester_worker_list = []

        # Redis access
        self.redis_cache = get_homedir() / self.conf.DB_DATA_PATH
        self.redis_storage = get_homedir() / self.conf.DB_DATA_PATH

        # Get sockets
        tmp_db_handler = database_start_stop.Database_StartStop(conf=conf)
        self.storage_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=True)
        self.cache_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=True)

    # ==================== ------ DB WORKERS ------- ====================

    # TODO : The four next functions have a LOT of duplicated code. Idea to factorize ?

    def start_n_adder_worker(self, db_conf: database_conf, nb=1):
        # Add N worker and return the current list of worker

        # Save current configuration
        tmp_db_conf_path = get_homedir() / "tmp_db_conf.json"
        json_import_export.save_json(db_conf, file_path=tmp_db_conf_path)

        for i in range(nb):
            self.logger.info(f"> Adding 'Adder' Worker {i} ...")

            init_date = datetime.datetime.now()

            # Open the worker subprocess with the configuration argument
            proc_worker = subprocess.Popen([str(self.adder_worker_path), '-c', str(tmp_db_conf_path.resolve())])

            # Store the reference to the worker
            self.adder_worker_list.append([proc_worker, init_date])

        return self.adder_worker_list

    def start_n_requester_worker(self, db_conf: database_conf, nb=1):
        # Add N worker and return the current list of worker

        # Save current configuration
        tmp_db_conf_path = get_homedir() / "tmp_db_conf.json"
        json_import_export.save_json(db_conf, file_path=tmp_db_conf_path)

        for i in range(nb):
            self.logger.info(f"> Adding 'Requester' Worker {i} ...")

            init_date = datetime.datetime.now()

            # Open the worker subprocess with the configuration argument
            proc_worker = subprocess.Popen([str(self.requester_worker_path), '-c', str(tmp_db_conf_path.resolve())])

            # Store the reference to the worker
            self.requester_worker_list.append([proc_worker, init_date])

        return self.requester_worker_list

    # ==================== ------ FEATURE WORKERS ------- ====================

    def start_n_feature_adder_worker(self, db_conf: database_conf, fe_conf: feature_extractor_conf, nb=1):
        # Save current configuration
        tmp_db_conf_path = get_homedir() / "tmp_db_conf.json"
        json_import_export.save_json(db_conf, file_path=tmp_db_conf_path)

        tmp_fe_conf_path = get_homedir() / "tmp_fe_conf.json"
        json_import_export.save_json(fe_conf, file_path=tmp_fe_conf_path)

        for i in range(nb):
            self.logger.info(f"> Adding 'Feature' Worker {i} with mode ADD ...")

            init_date = datetime.datetime.now()

            # Open the worker subprocess with the configuration argument
            proc_worker = subprocess.Popen([str(self.feature_worker_path), '-c', str(tmp_db_conf_path.resolve()), '-cfe', str(tmp_fe_conf_path.resolve()), '-m', "ADD"])

            # Store the reference to the worker
            self.feature_adder_worker_list.append([proc_worker, init_date])

        return self.feature_adder_worker_list

    def start_n_feature_request_worker(self, db_conf: database_conf, fe_conf: feature_extractor_conf, nb=1):

        # Save current configuration
        tmp_db_conf_path = get_homedir() / "tmp_db_conf.json"
        json_import_export.save_json(db_conf, file_path=tmp_db_conf_path)

        tmp_fe_conf_path = get_homedir() / "tmp_fe_conf.json"
        json_import_export.save_json(fe_conf, file_path=tmp_fe_conf_path)

        for i in range(nb):
            self.logger.info(f"> Adding 'Feature' Worker {i} with mode REQUEST ...")

            init_date = datetime.datetime.now()

            # Open the worker subprocess with the configuration argument
            proc_worker = subprocess.Popen([str(self.feature_worker_path), '-c', str(tmp_db_conf_path.resolve()), '-cfe', str(tmp_fe_conf_path.resolve()), '-m', "REQUEST"])

            # Store the reference to the worker
            self.feature_requester_worker_list.append([proc_worker, init_date])

        return self.feature_requester_worker_list


    # ==================== ------ UTLITIES ON WORKERS ------- ====================

    def request_shutdown(self):
        # Post a HALT key in all redis instance. Worker should react "quickly" and stop themselves
        self.cache_db.set("halt", True)
        self.storage_db.set("halt", True)

    def check_worker(self):
        # Check if workers are alive, and return True if all worker are down

        all_ended = True

        worker_list = [{"list":self.adder_worker_list, "name":"Adder_worker"},      # ==== CHECK for ADDER WORKERS
                       {"list":self.requester_worker_list, "name":"Request_worker"},  # ==== CHECK for REQUESTER WORKERS
                       {"list":self.feature_adder_worker_list, "name":"Feature_Adder_worker"},   # ==== CHECK for FEATURE ADDER WORKERS
                       {"list":self.feature_requester_worker_list, "name":"Feature_Requester_worker"},]   # ==== CHECK for FEATURE REQUEST WORKERS

        # For all kind of workers
        for curr_worker_list in worker_list :
            self.logger.info(f"{len(curr_worker_list['list'])} worker(s) are {curr_worker_list['name']}")

            for i, curr_proc in enumerate(curr_worker_list['list']):
                curr_str = f"==> Worker {i} : Launched on {curr_proc[1]}"

                if curr_proc[0].poll() is None:
                    curr_str += " status : running ..."
                    all_ended = False
                else:
                    curr_str += " status : terminated or ended ..."

                self.logger.info(curr_str)

        return all_ended

