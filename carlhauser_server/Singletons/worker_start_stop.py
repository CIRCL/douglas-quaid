#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
from typing import List

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Helpers.Processus.processus_list as processus_list
import carlhauser_server.Helpers.Processus.worker_processus as worker_processus
from carlhauser_server.Helpers.Processus.worker_types import WorkerTypes as workertype
from common.environment_variable import get_homedir
from carlhauser_server.Singletons.template_singleton import Singleton

# ==================== ------ PERSONAL LIBRARIES ------- ====================

sys.path.append(os.path.abspath(os.path.pardir))


# ==================== ------ PATHS ------- ====================


class Worker_StartStop(object, metaclass=Singleton):
    # Singleton class that handle database access
    # _instance = None

    def __init__(self, db_conf: database_conf):
        # STD attributes
        self.db_conf = db_conf
        self.logger = logging.getLogger(__name__)
        self.logger.critical("SINGLETON CREATED (worker start stop)")

        # Specific attributes
        # self.worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'DatabaseAccessor', 'datanase_worker.py')
        self.adder_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'DatabaseAccessor', 'database_adder.py')
        self.requester_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'DatabaseAccessor', 'database_requester.py')
        self.feature_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'FeatureExtractor', 'feature_worker.py')
        self.flask_worker_path = get_homedir() / pathlib.Path('carlhauser_server', 'API', 'API_server.py')

        # Mapping from workertype to worker list
        self.mapping = {
            workertype.ADDER: processus_list.ProcessusList("Adder Worker", []),
            workertype.REQUESTER: processus_list.ProcessusList("Requester Worker", []),
            workertype.FEATURE_ADDER: processus_list.ProcessusList("Feature Adder Worker", []),
            workertype.FEATURE_REQUESTER: processus_list.ProcessusList("Feature Requester Worker", []),
            workertype.FLASK: processus_list.ProcessusList("Flask/API Worker", []),
        }

        # Reference to database_start_stop
        # self.db_start_stop = database_start_stop.Database_StartStop(None, False)  # It's a singleton .. so we should get its instance

    def get_processes_list(self, name: workertype) -> processus_list.ProcessusList:
        # returns a workers list
        return self.mapping[name]

    def get_all_processes_lists(self) -> List[processus_list.ProcessusList]:
        # returns a list of workers lists
        return list(self.mapping.values())

    # ==================== ------ GENERIC WORKERS ------- ====================

    def start_and_add_n_worker(self, worker_type: workertype,
                               db_conf: database_conf = None, dist_conf: distance_engine_conf = None, fe_conf: feature_extractor_conf = None, ws_conf: webservice_conf = None,
                               nb=1):
        # Add <nb> workers to the <list_to_add> workers lists, by launching <worker_path> as a subprocess and giving <XX_conf> as parameters (many at once is possible)

        # Parse the worker type
        mode = None  # {"ADD", "REQUEST"}
        self.logger.debug(f"Worker start/stop is asked to create {worker_type}")
        if worker_type == workertype.ADDER:
            worker_path = self.adder_worker_path

        elif worker_type == workertype.REQUESTER:
            worker_path = self.requester_worker_path

        elif worker_type == workertype.FEATURE_REQUESTER:
            worker_path = self.feature_worker_path
            mode = "REQUEST"

        elif worker_type == workertype.FEATURE_ADDER:
            worker_path = self.feature_worker_path
            mode = "ADD"

        elif worker_type == workertype.FLASK:
            worker_path = self.flask_worker_path

        else:
            raise Exception("Worker type not handled.")

        # Add n workers wih this configuration
        for i in range(nb):
            self.logger.info(f"Adding {worker_path.name} Worker {i} ...")

            # Create the worker
            tmp_worker_process = worker_processus.WorkerProcessus(worker_path)

            # Launch it, with configurations
            tmp_worker_process.launch(db_conf, dist_conf, fe_conf, ws_conf, mode)

            # Store its reference (as new member of the list of the good type)
            self.mapping.get(worker_type).append(tmp_worker_process)

    def stop_list_worker(self, worker_type: workertype):
        self.mapping.get(worker_type).kill_all_processus()

    # ==================== ------ UTLITIES ON WORKERS ------- ====================
    def wait_for_worker_shutdown(self, max_wait=60):
        # Send signal to all processes to stop (via redis database). Wait while processes are still running,
        # in the limit of a maximal amount of time. Send back a boolean to notify if all workers had been stopped, or not.
        all_have_stopped = True

        self.logger.warning(f"Waiting for workers to stop. Gracetime of {max_wait}s per worker ... ")
        for curr_worker_list in list(self.mapping.values()):

            self.logger.debug(f"Waiting {curr_worker_list.list_name} workers ... ")
            are_stopped = curr_worker_list.wait_until_all_stopped(timeout=max_wait)

            if not are_stopped:
                # If waiting has timeouted, return
                self.logger.warning("Some still running, even after max waiting time. Time-out-ed")
                all_have_stopped = False
                break

        return all_have_stopped

    def get_list_running_workers(self):
        # Returns the list of currently running workers (all types)
        running_workers = []

        # For each list of process, and then each process, check if it's alive
        for curr_worker_list in list(self.mapping.values()):
            running_workers.extend(curr_worker_list.get_running_processus())

        return running_workers

    def is_there_alive_workers(self):
        # Check if workers are alive, and return True if all worker are down

        all_ended = True

        # For all kind of workers
        for curr_worker_list in list(self.mapping.values()):
            all_ended_for_this_list = curr_worker_list.is_there_alive_workers()

            if not all_ended_for_this_list:
                # We found some processes that haven't finished
                all_ended = False
                break

        return all_ended

    # ==================== ------ SHUTDOWN WORKERS ------- ====================
    '''
    def shutdown_nicely_and_then_not(self, max_wait=60):
        self.request_shutdown()
        self.wait_for_worker_shutdown(max_wait)

        # If exited previous loop, maybe all workers are shutdown
        if len(self.get_list_running_workers()) == 0:
            self.logger.info("All processus had been stopped")
            return True

        # Or exited previous loop due to timeout : some may be still running
        else:
            self.logger.info("Actual processus state : ")
            self.is_there_alive_workers()

            self.logger.warning("'Waiting for workers to stop' has expired. Killing processus ... ")

            # Time out = kill all processus and exit
            self.kill_and_flush_workers()

            return len(self.get_list_running_workers()) == 0


    def request_shutdown(self):
        # Post a HALT key in all redis instance. Worker should react "quickly" and stop themselves
        self.db_start_stop.request_workers_shutdown()

        # TODO : to review = send the message to database start stop
        # self.cache_db.set("halt", "true")
        # self.storage_db.set("halt", "true")
    '''


    def kill_and_flush_workers(self):
        # Kill each worker and then empty lists. Very violent.
        for curr_workers_list in list(self.mapping.values()):
            curr_workers_list.kill_all_processus()
            curr_workers_list.flush()

    # ==================== ------ DB WORKERS ------- ====================

    '''
    def start_n_adder_worker(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.adder_worker_path, list_to_add=self.adder_worker_list.processus_list,
                                    db_conf=db_conf, dist_conf=dist_conf, fe_conf=fe_conf, nb=nb)

        # return self.adder_worker_list

    def start_n_requester_worker(self, db_conf: database_conf, dist_conf: distance_engine_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.requester_worker_path, list_to_add=self.requester_worker_list.processus_list,
                                    db_conf=db_conf, dist_conf=dist_conf, fe_conf=fe_conf, nb=nb)

        # return self.requester_worker_list

    def stop_adder_worker(self):
        self.adder_worker_list.kill_all_processus()

    def stop_requester_worker(self):
        self.requester_worker_list.kill_all_processus()

    # ==================== ------ FEATURE WORKERS ------- ====================

    def start_n_feature_adder_worker(self, db_conf: database_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.feature_worker_path, list_to_add=self.feature_adder_worker_list.processus_list,
                                    db_conf=db_conf, fe_conf=fe_conf, mode="ADD", nb=nb)

        # return self.feature_adder_worker_list

    def start_n_feature_request_worker(self, db_conf: database_conf, fe_conf: feature_extractor_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.feature_worker_path, list_to_add=self.feature_requester_worker_list.processus_list,
                                    db_conf=db_conf, fe_conf=fe_conf, mode="REQUEST", nb=nb)

        # return self.feature_requester_worker_list

    def stop_feature_adder_worker(self):
        self.feature_adder_worker_list.kill_all_processus()

    def stop_feature_request_worker(self):
        self.feature_requester_worker_list.kill_all_processus()

    # ==================== ------ FLASK/API WORKERS ------- ====================

    def start_n_flask_worker(self, db_conf: database_conf, ws_conf: webservice_conf, nb=1):
        # Add N worker and return the current list of worker
        self.start_and_add_n_worker(self.flask_worker_path, list_to_add=self.flask_worker_list.processus_list,
                                    db_conf=db_conf, ws_conf=ws_conf, nb=nb)

        # return self.flask_worker_list

    def stop_flask_workers(self):
        self.flask_worker_list.kill_all_processus()
    '''

    '''
    self.logger.info(f"{len(curr_worker_list.processus_list)} worker(s) are presents in {curr_worker_list.list_name}.")

    for i, curr_proc in enumerate(curr_worker_list.processus_list):
        curr_str = f"==> Worker {i} : Launched on {curr_proc}"

        if curr_proc.is_running():
            curr_str += " status : running ..."
            all_ended = False
        else:
            curr_str += " status : terminated or ended ..."

        self.logger.info(curr_str)
    '''


'''
start_time = time.time()
self.logger.warning("Waiting for workers to stop ... ")

# Wait for all workers to terminate
while len(self.get_list_running_workers()) != 0 and (time.time() - start_time) < max_wait:
    time.sleep(5)
    self.logger.warning(" Some still running...")

# If exited previous loop, maybe all workers are shutdown
if len(self.get_list_running_workers()) == 0:
    self.logger.info("All processus had been stopped")
    return True

# Or exited previous loop due to timeout : some may be still running
else:
    self.logger.info("Actual processus state ... ")
    self.is_there_alive_workers()

    self.logger.warning("Waiting for workers to stop expired. Killing processus ... ")

    # Time out = kill all processus and exit
    for curr_worker_list in list(self.mapping.values()):
        curr_worker_list.kill_all_processus()

    return len(self.get_list_running_workers()) == 0
'''

'''
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
'''

'''
# Redis access
self.redis_cache = get_homedir() / self.db_conf.DB_DATA_PATH
self.redis_storage = get_homedir() / self.db_conf.DB_DATA_PATH

# Get sockets
tmp_db_handler = database_start_stop.Database_StartStop(db_conf=db_conf)
self.storage_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('storage'), decode_responses=True)
self.cache_db = redis.Redis(unix_socket_path=tmp_db_handler.get_socket_path('cache'), decode_responses=True)
'''

'''
init_date = datetime.datetime.now()

# Open the worker subprocess with the configuration argument
proc_worker = subprocess.Popen(arg_list) # TODO : Is it needed ? TO_CHANGE , stdout=sys.stdout, stderr=sys.stderr, preexec_fn=os.setsid)
# ,stderr = subprocess.PIPE ?
# proc_worker.communicate()
'''

# Worker lists
# self.worker_list = []
'''
self.adder_worker_list = processus_list.ProcessusList("Adder Worker", [])
self.requester_worker_list = processus_list.ProcessusList("Requester Worker", [])
self.feature_adder_worker_list = processus_list.ProcessusList("Feature Adder Worker", [])
self.feature_requester_worker_list = processus_list.ProcessusList("Feature Requester Worker", [])
self.flask_worker_list = processus_list.ProcessusList("Flask/API Worker", [])
'''
