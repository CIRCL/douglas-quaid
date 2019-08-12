#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pathlib
import time
from enum import Enum, auto
from typing import List

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Processus.processus_list as processus_list
import carlhauser_server.Processus.worker_process as worker_processus
from carlhauser_server.Singletons.singleton import Singleton
from common.environment_variable import get_homedir, JSON_parsable_Enum
from common.environment_variable import load_server_logging_conf_file
from carlhauser_client.API.extended_api import Extended_API

load_server_logging_conf_file()


class WorkerTypes(JSON_parsable_Enum, Enum):
    ADDER = auto()
    REQUESTER = auto()
    FEATURE_ADDER = auto()
    FEATURE_REQUESTER = auto()
    FLASK = auto()


class Worker_StartStop(object, metaclass=Singleton):
    """
    Singleton class that handle workers and processses management
    """

    def __init__(self, db_conf: database_conf.Default_database_conf):
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
            WorkerTypes.ADDER: processus_list.ProcessesList("Adder Worker", []),
            WorkerTypes.REQUESTER: processus_list.ProcessesList("Requester Worker", []),
            WorkerTypes.FEATURE_ADDER: processus_list.ProcessesList("Feature Adder Worker", []),
            WorkerTypes.FEATURE_REQUESTER: processus_list.ProcessesList("Feature Requester Worker", []),
            WorkerTypes.FLASK: processus_list.ProcessesList("Flask/API Worker", []),
        }

    def get_processes_list(self, name: WorkerTypes) -> processus_list.ProcessesList:
        """
        Returns the workers list of the asked worker type
        :param name: The type of worker, to return the list of processes
        :return: A list of processes in a ProccessusList Object
        """
        return self.mapping[name]

    def get_all_processes_lists(self) -> List[processus_list.ProcessesList]:
        """
        Returns all lists of workers lists
        :return: A list of ProcessesList
        """
        return list(self.mapping.values())

    # ==================== ------ GENERIC WORKERS ------- ====================

    def start_and_add_n_worker(self, worker_type: WorkerTypes,
                               db_conf: database_conf = None,
                               dist_conf: distance_engine_conf = None,
                               fe_conf: feature_extractor_conf = None,
                               ws_conf: webservice_conf = None,
                               nb=1):
        """
        Add <nb> workers to the <list_to_add> workers lists, by launching <worker_path>
        as a subprocess and giving <XX_conf> as parameters (many at once is possible)
        :param worker_type: type of work to launch
        :param db_conf: configuration file
        :param dist_conf: configuration file
        :param fe_conf: configuration file
        :param ws_conf: configuration file
        :param nb: Number of worker of this type to launch
        :return: Nothing
        """

        # Parse the worker type
        mode = None  # {"ADD", "REQUEST"}
        self.logger.debug(f"Worker start/stop is asked to create {worker_type}")

        if worker_type == WorkerTypes.ADDER:
            worker_path = self.adder_worker_path
        elif worker_type == WorkerTypes.REQUESTER:
            worker_path = self.requester_worker_path
        elif worker_type == WorkerTypes.FEATURE_REQUESTER:
            worker_path = self.feature_worker_path
            mode = "REQUEST"
        elif worker_type == WorkerTypes.FEATURE_ADDER:
            worker_path = self.feature_worker_path
            mode = "ADD"
        elif worker_type == WorkerTypes.FLASK:
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

            # Monitor the worker if asked to
            if self.db_conf.MONITOR_WORKER:
                self.logger.info(f"Monitoring is being added on the Worker PID")
                tmp_worker_process.monitor_worker(self.db_conf.MONITOR_RATE)

            # Store its reference (as new member of the list of the good type)
            self.mapping.get(worker_type).append(tmp_worker_process)

    def stop_list_worker(self, worker_type: WorkerTypes) -> bool:
        """
        Stop the worker of the provided type
        :param worker_type: The workers to stop
        :return: True if workers successfuly stop, False otherwise
        """
        return self.mapping.get(worker_type).kill_all_processus()

    # ==================== ------ UTLITIES ON WORKERS ------- ====================
    def wait_for_worker_startup(self, max_wait=60):

        # TODO ! other workers !
        time.sleep(1)

        return self.wait_for_webservice_worker_startup()

    def wait_for_webservice_worker_startup(self, max_wait=60):

        # Get the API as client
        api = Extended_API.get_api()

        # Starting count-down
        start_time = time.time()
        self.logger.info(f"Checking if webservice worker is online. Start polling ...")

        # While the answer is not ready or we haven't timed-out
        time_out = False
        pinged = False
        while not pinged and not time_out:
            try:
                pinged = api.ping_server()
            except Exception as e:
                # Not ready yet, wait a bit
                self.logger.info(f"Webservice worker not online yet, waiting ...{e}")
                time.sleep(2)

            # Compute if we are already in time out
            time_out = (abs(time.time() - start_time) > max_wait and max_wait != -1)

            if time_out:
                self.logger.info(f"Webservice worker is still not online. Time out ! ...")
                return False

        # Ready !
        self.logger.info(f"Webservice worker is detected online.")

        return True

    def wait_for_worker_shutdown(self, max_wait=60) -> bool:
        """
        Send signal to all processes to stop (via redis database). Wait while processes are still running,
        in the limit of a maximal amount of time. Send back a boolean to notify if all workers had been stopped, or not.
        :param max_wait: maximum waiting time for each worker
        :return: True if all stopped, False otherwise
        """

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

    def get_list_running_workers(self) -> List[worker_processus.WorkerProcessus]:
        """
        Returns the list of currently running workers (all types)
        :return: List of running processes
        """

        running_workers = []

        # For each list of process, and then each process, check if it's alive
        for curr_worker_list in list(self.mapping.values()):
            running_workers.extend(curr_worker_list.get_running_processus())

        return running_workers

    def is_there_alive_workers(self):
        """
        Check if workers are alive, and return True if all workers are down
        :return: True if at least a worker is alive, Fale otherwise
        """

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
    def kill_and_flush_workers(self):
        """
        Kill each worker and then empty lists. Very violent. Use at your own risks :)
        :return: Nothing. Void and Death only.
        """

        for curr_workers_list in list(self.mapping.values()):
            curr_workers_list.kill_all_processus()
            curr_workers_list.flush()
