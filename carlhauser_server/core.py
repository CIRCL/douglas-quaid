#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import signal
import sys
import time
import traceback

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Helpers.environment_variable import get_homedir

import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.Configuration.database_conf as database_conf

import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf

import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf

import carlhauser_server.Helpers.worker_start_stop as worker_start_stop
import carlhauser_server.Helpers.template_singleton as template_singleton
from carlhauser_server.Helpers.Processus.worker_types import WorkerTypes as workertype

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_server", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class launcher_handler(metaclass=template_singleton.Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Create configuration
        self.db_conf = database_conf.Default_database_conf()
        self.ws_conf = webservice_conf.Default_webservice_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()
        self.di_conf = distance_engine_conf.Default_distance_engine_conf()

        # Handlers
        self.db_handler = None
        self.worker_handler = None

    def launch(self):
        # Launch elements
        self.start_database(wait=True)  # Wait for launch

        self.start_adder_workers()
        self.start_requester_workers()
        self.start_feature_workers()
        self.start_webservice()

        self.check_worker()

        # TODO : # If the webservice is down, then we want to shutdown everything
        # self.shutdown_workers(self.db_conf)
        # self.check_worker(self.db_conf)

    def stop(self):

        # Shutdown Flask worker
        self.stop_webservice()

        # Shutdown workers
        if not self.check_worker():
            self.shutdown_workers()
        else:
            self.logger.warning("All workers are already stopped.")

        # Shutdown database
        self.stop_database(wait=True)  # Wait for stop

    # ==================== ------ DB ------- ====================
    def check_db_handler(self):
        # Create a Singleton instance of DB handler if none is present
        if self.db_handler is None:
            self.logger.info("DB Handler not present in core. Creation of DB handler singleton ...")
            self.db_handler = database_start_stop.Database_StartStop(db_conf=self.db_conf)

    def check_worker_handler(self):
        # Create a Singleton instance of DB handler if none is present
        if self.worker_handler is None:
            self.logger.info("Worker Handler not present in core. Creation of Worker handler singleton ...")
            self.worker_handler = worker_start_stop.Worker_StartStop(db_conf=self.db_conf)

    def start_database(self, wait=False):
        self.check_db_handler()
        self.logger.info(f"Launching redis database (x2) ...")  # (cache and storage)
        self.db_handler.launch_all_redis()

        if wait:
            if self.db_handler.wait_until_all_redis_running():
                self.logger.info(f"Redis databases successfully launched (ping verified)")
            else:
                self.logger.critical(f"Redis databases are NOT launched (ping verified)")
                raise Exception("Impossible to connect to database : timeout while waiting for redis to run")

    def stop_database(self, wait=False):
        self.check_db_handler()
        self.logger.info(f"Stopping redis database (x2) ...")  # (cache and storage)
        self.db_handler.stop_all_redis()

        if wait:
            if self.db_handler.wait_until_all_redis_stopped():
                self.logger.info(f"Redis database successfully stopped (ping verified)")
            else:
                self.logger.critical(f"Redis database had NOT stopped (ping verified)")

    def flush_db(self):
        self.check_db_handler()
        self.logger.info(f"Flushing redis database (x2) ...")  # (cache and storage)
        self.db_handler.flush_all_redis()

    # ==================== ------ DB WORKERS ------- ====================

    def start_adder_workers(self):
        self.check_worker_handler()
        self.logger.info(f"Launching to_add worker (x{self.db_conf.ADDER_WORKER_NB}) ...")
        self.worker_handler.start_and_add_n_worker(worker_type=workertype.ADDER,
                                                   db_conf=self.db_conf, dist_conf=self.di_conf, fe_conf=self.fe_conf,
                                                   nb=self.db_conf.ADDER_WORKER_NB)

    def start_requester_workers(self):
        self.check_worker_handler()
        self.logger.info(f"Launching to_request worker (x{self.db_conf.REQUESTER_WORKER_NB}) ...")
        self.worker_handler.start_and_add_n_worker(worker_type=workertype.REQUESTER,
                                                   db_conf=self.db_conf, dist_conf=self.di_conf, fe_conf=self.fe_conf,
                                                   nb=self.db_conf.REQUESTER_WORKER_NB)

    # ==================== ------ FEATURE WORKERS ------- ====================

    def start_feature_workers(self):
        self.check_worker_handler()
        self.logger.info(f"Launching feature worker (x{self.fe_conf.FEATURE_ADDER_WORKER_NB} + x{self.fe_conf.FEATURE_REQUEST_WORKER_NB}) ...")
        self.worker_handler.start_and_add_n_worker(worker_type=workertype.FEATURE_ADDER,
                                                   db_conf=self.db_conf, fe_conf=self.fe_conf,
                                                   nb=self.fe_conf.FEATURE_ADDER_WORKER_NB)
        self.worker_handler.start_and_add_n_worker(worker_type=workertype.FEATURE_REQUESTER,
                                                   db_conf=self.db_conf, fe_conf=self.fe_conf,
                                                   nb=self.fe_conf.FEATURE_REQUEST_WORKER_NB)

    # ==================== ------ WEBSERVICE ------- ====================

    def start_webservice(self):
        self.check_worker_handler()
        self.logger.info(f"Launching webservice ...")

        # Create configuration file
        self.ws_conf.CERT_FILE = self.ws_conf.CERT_FILE.resolve()
        self.ws_conf.KEY_FILE = self.ws_conf.KEY_FILE.resolve()
        self.worker_handler.start_and_add_n_worker(worker_type=workertype.FLASK,
                                                   db_conf=self.db_conf, ws_conf=self.ws_conf,
                                                   nb=1)

    def stop_webservice(self):
        self.check_worker_handler()
        self.logger.info(f"Stopping webservice ...")
        self.worker_handler.stop_list_worker(worker_type=workertype.FLASK)

    # ==================== ------ UTLITIES ON WORKERS ------- ====================

    def check_worker(self):
        self.check_worker_handler()
        self.logger.info(f"Checking for workers ...")
        return self.worker_handler.is_there_alive_workers()

    def shutdown_workers(self):
        self.check_worker_handler()
        self.logger.info(f"Requesting workers to stop ...")
        self.db_handler.request_workers_shutdown()
        return self.worker_handler.wait_for_worker_shutdown()

    def flush_workers(self):
        self.check_worker_handler()
        self.logger.info(f"Requesting workers to stop ...")
        return self.worker_handler.kill_and_flush_workers()


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    # signal.signal(signal.SIGINT, original_sigint) # TODO : To put back ?

    try:
        stopper = launcher_handler()
        print("Wait for the extinction ... ")
        stopper.stop()
        sys.exit(1)

    except KeyboardInterrupt:
        print("You should be nicer to carl-hauser.")
        sys.exit(1)

    # restore the exit gracefully handler here
    # signal.signal(signal.SIGINT, exit_gracefully) # TODO : To put back ?


if __name__ == '__main__':
    launcher = launcher_handler()

    try:
        # Setting SIGINT handler
        # original_sigint = signal.getsignal(signal.SIGINT)  # Storing original
        signal.signal(signal.SIGINT, exit_gracefully)  # Setting custom
        launcher.launch()
        time.sleep(1)

        do_stop = False
        while not do_stop:
            print("Press any key to stop ... ")
            input()
            print("Are you sure you want to stop ? [yes/no] ")
            value = input()
            if value == "yes":
                do_stop = True

        launcher.stop()

    except KeyboardInterrupt:
        print('Interruption detected')
        try:
            print('Handling interruptions ...')
            launcher.stop()
            # TODO : Handle interrupt and shutdown, and clean ...
            sys.exit(0)
        except SystemExit:
            traceback.print_exc(file=sys.stdout)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(f'Critical problem during execution {e}')
        launcher.stop()
        sys.exit(0)

'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage backend DBs.')
    parser.add_argument("--start", action='store_true', default=False, help="Start all")
    parser.add_argument("--stop", action='store_true', default=False, help="Stop all")
    parser.add_argument("--status", action='store_true', default=True, help="Show status")
    args = parser.parse_args()

    if args.start:
        launch_all()
    if args.stop:
        stop_all()
    if not args.stop and args.status:
        check_all()
'''
