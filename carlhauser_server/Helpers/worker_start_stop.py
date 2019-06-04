#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import subprocess
import sys
import time
from typing import List

import redis

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.template_singleton import Singleton
from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Helpers.json_import_export as json_import_export
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Helpers.database_start_stop as database_start_stop

import carlhauser_server.Helpers.Processus.worker_processus as worker_processus
import carlhauser_server.Helpers.Processus.processus_list as processus_list


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
        self.flask_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'API', 'API_server.py')

        # Worker lists
        # self.worker_list = []
        self.adder_worker_list = processus_list.ProcessusList("Adder Worker", [])
        self.requester_worker_list = processus_list.ProcessusList("Requester Worker", [])
        self.feature_adder_worker_list = processus_list.ProcessusList("Feature Adder Worker", [])
        self.feature_requester_worker_list = processus_list.ProcessusList("Feature Requester Worker", [])
        self.flask_worker_list = processus_list.ProcessusList("Flask/API Worker", [])
        self.list_of_workers_list = [self.adder_worker_list, self.requester_worker_list, self.feature_adder_worker_list,
                                     self.feature_requester_worker_list, self.flask_worker_list]

        # Redis access
        self.redis_cache = get_homedir() / self.conf.DB_DATA_PATH
        self.redis_storage = get_homedir() / self.conf.DB_DATA_PATH

        # Get sockets
        tmp_db_handler = database_start_stop.Database_StartStop(conf=conf)
        self.storage_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=True)
        self.cache_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=True)

    # ==================== ------ GENERIC WORKERS ------- ====================

    def start_and_add_n_worker(self, worker_path: pathlib.Path, list_to_add: List,
                               db_conf: database_conf = None, dist_conf: distance_engine_conf = None, fe_conf: feature_extractor_conf = None, ws_conf: webservice_conf = None,
                               mode=None,
                               nb=1):
        # Add <nb> workers to the <list_to_add> workers lists, by launching <worker_path> as a subprocess and giving <XX_conf> as parameters (many at once is possible)
        arg_list = [str(worker_path)]

        # Save current configuration in files
        if db_conf is not None:
            tmp_db_conf_path = get_homedir() / "tmp_db_conf.json"
            json_import_export.save_json(db_conf, file_path=tmp_db_conf_path)
            arg_list.append('-dbc')
            arg_list.append(str(tmp_db_conf_path.resolve()))

        if dist_conf is not None:
            tmp_dist_conf_path = get_homedir() / "tmp_dist_conf.json"
            json_import_export.save_json(dist_conf, file_path=tmp_dist_conf_path)
            arg_list.append('-distc')
            arg_list.append(str(tmp_dist_conf_path.resolve()))

        if fe_conf is not None:
            tmp_fe_conf_path = get_homedir() / "tmp_fe_conf.json"
            json_import_export.save_json(fe_conf, file_path=tmp_fe_conf_path)
            arg_list.append('-fec')
            arg_list.append(str(tmp_fe_conf_path.resolve()))

        if ws_conf is not None:
            tmp_ws_conf_path = get_homedir() / "tmp_ws_conf.json"
            json_import_export.save_json(ws_conf, file_path=tmp_ws_conf_path)
            arg_list.append('-wsc')
            arg_list.append(str(tmp_ws_conf_path.resolve()))

        if mode is not None:
            arg_list.append('-m')
            arg_list.append(mode)

        # Add n workers wih this configuration
        for i in range(nb):
            self.logger.info(f"> Adding {worker_path.name} Worker {i} ...")

            init_date = datetime.datetime.now()

            # Open the worker subprocess with the configuration argument
            proc_worker = subprocess.Popen(arg_list, stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid)
            # ,stderr = subprocess.PIPE ?
            # proc_worker.communicate()

            # Store the reference to the worker
            list_to_add.append(worker_processus.WorkerProcessus(proc_worker, init_date))

    # ==================== ------ DB WORKERS ------- ====================

    def start_n_adder_worker(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.adder_worker_path, list_to_add=self.adder_worker_list.processus_list,
                                    db_conf=db_conf, dist_conf=dist_conf, fe_conf=fe_conf, nb=nb)

        return self.adder_worker_list

    def start_n_requester_worker(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.requester_worker_path, list_to_add=self.requester_worker_list.processus_list,
                                    db_conf=db_conf, dist_conf=dist_conf, fe_conf=fe_conf, nb=nb)

        return self.requester_worker_list

    def stop_adder_worker(self):
        self.adder_worker_list.kill_all_processus()

    def stop_requester_worker(self):
        self.requester_worker_list.kill_all_processus()

    # ==================== ------ FEATURE WORKERS ------- ====================

    def start_n_feature_adder_worker(self, db_conf: database_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.feature_worker_path, list_to_add=self.feature_adder_worker_list.processus_list,
                                    db_conf=db_conf, fe_conf=fe_conf, mode="ADD", nb=nb)

        return self.feature_adder_worker_list

    def start_n_feature_request_worker(self, db_conf: database_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.feature_worker_path, list_to_add=self.feature_requester_worker_list.processus_list,
                                    db_conf=db_conf, fe_conf=fe_conf, mode="REQUEST", nb=nb)

        return self.feature_requester_worker_list

    def stop_feature_adder_worker(self):
        self.feature_adder_worker_list.kill_all_processus()

    def stop_feature_request_worker(self):
        self.feature_requester_worker_list.kill_all_processus()

    # ==================== ------ FLASK/API WORKERS ------- ====================

    def start_n_flask_worker(self, db_conf: database_conf, ws_conf: webservice_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.flask_worker_path, list_to_add=self.flask_worker_list.processus_list,
                                    db_conf=db_conf, ws_conf=ws_conf, nb=nb)

        return self.flask_worker_list

    def stop_flask_workers(self):
        self.flask_worker_list.kill_all_processus()

    # ==================== ------ UTLITIES ON WORKERS ------- ====================
    def wait_for_worker_shutdown(self):
        # Send signal to all processes to stop (via redis database). Wait while processes are still running,
        # in the limit of a maximal amount of time. Send back a boolean to notify if all workers had been stopped, or not.
        self.request_shutdown()

        MAX_TIME = 60  # 60 sec
        start_time = time.time()

        self.logger.warning("Waiting for workers to stop ... ")
        # Wait for all workers to terminate
        while len(self.get_list_running_workers()) != 0 and (time.time() - start_time) < MAX_TIME:
            time.sleep(5)
            self.logger.warning(" Some still running...")

        self.logger.warning("Waiting for workers to stop expired. Killing processus ... ")
        # Time out = kill all processus and exit
        for curr_worker_list in self.list_of_workers_list:
            curr_worker_list.kill_all_processus()

        return len(self.get_list_running_workers()) == 0

    def get_list_running_workers(self):
        # Returns the list of currently running workers
        running_workers = []

        # For each list of process, and then each process, check if it's alive
        for curr_worker_list in self.list_of_workers_list:
            running_workers.extend(curr_worker_list.get_running_processus())

        return running_workers

    def check_workers(self):
        # Check if workers are alive, and return True if all worker are down

        all_ended = True

        # For all kind of workers
        for curr_worker_list in self.list_of_workers_list:
            self.logger.info(f"{len(curr_worker_list.processus_list)} worker(s) are presents in {curr_worker_list.list_name}.")

            for i, curr_proc in enumerate(curr_worker_list.processus_list):
                curr_str = f"==> Worker {i} : Launched on {curr_proc}"

                if curr_proc.is_running():
                    curr_str += " status : running ..."
                    all_ended = False
                else:
                    curr_str += " status : terminated or ended ..."

                self.logger.info(curr_str)

        return all_ended

    # ==================== ------ SHUTDOWN WORKERS ------- ====================

    def request_shutdown(self):
        # Post a HALT key in all redis instance. Worker should react "quickly" and stop themselves
        self.cache_db.set("halt", "true")
        self.storage_db.set("halt", "true")

    def flush_workers(self):
        # Kill each worker and then empty lists. Very violent.
        for curr_worker_list in self.list_of_workers_list:
            curr_worker_list.flush_all_processus()
