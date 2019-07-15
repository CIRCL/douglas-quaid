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

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import common.ImportExport.json_import_export as json_import_export
from carlhauser_server.DatabaseAccessor.arg_parser import ConfArgs
from common.environment_variable import get_homedir

# ==================== ------ PERSONAL LIBRARIES ------- ====================

sys.path.append(os.path.abspath(os.path.pardir))


# ==================== ------ PATHS ------- ====================

# Small class to handle processus
class WorkerProcessus:
    def __init__(self, worker_path: pathlib.Path):
        self.worker_path: pathlib.Path = worker_path
        self.process: subprocess.Popen = None  # processus: subprocess.Popen
        self.start_time = None

        self.logger = logging.getLogger(__name__)

    def launch(self, db_conf: database_conf.Default_database_conf = None,
               dist_conf: distance_engine_conf.Default_distance_engine_conf = None,
               fe_conf: feature_extractor_conf.Default_feature_extractor_conf = None,
               ws_conf: webservice_conf.Default_webservice_conf = None,
               mode=None):
        """
        Construct an argument list and launch the process.
        :param db_conf: configuration file
        :param dist_conf: configuration file
        :param fe_conf: configuration file
        :param ws_conf: configuration file
        :param mode:  configuration element
        :return: Nothing
        """
        # Construct an argument list to be 'popen' as a new process
        arg_list = [str(self.worker_path)]

        # Save current configuration in files
        # Using self.worker_path.parent
        if db_conf is not None:
            tmp_db_conf_path = get_homedir() / "tmp_db_conf.json"
            json_import_export.save_json(db_conf, file_path=tmp_db_conf_path)
            arg_list.append(ConfArgs.DB_CONF_ARG)
            arg_list.append(str(tmp_db_conf_path.resolve()))

        if dist_conf is not None:
            tmp_dist_conf_path = get_homedir() / "tmp_dist_conf.json"
            json_import_export.save_json(dist_conf, file_path=tmp_dist_conf_path)
            arg_list.append(ConfArgs.DIST_CONF_ARG)
            arg_list.append(str(tmp_dist_conf_path.resolve()))

        if fe_conf is not None:
            tmp_fe_conf_path = get_homedir() / "tmp_fe_conf.json"
            json_import_export.save_json(fe_conf, file_path=tmp_fe_conf_path)
            arg_list.append(ConfArgs.FE_CONF_ARG)
            arg_list.append(str(tmp_fe_conf_path.resolve()))

        if ws_conf is not None:
            tmp_ws_conf_path = get_homedir() / "tmp_ws_conf.json"
            json_import_export.save_json(ws_conf, file_path=tmp_ws_conf_path)
            arg_list.append(ConfArgs.WS_CONF_ARG)
            arg_list.append(str(tmp_ws_conf_path.resolve()))

        if mode is not None:
            arg_list.append(ConfArgs.MODE_ARG)
            arg_list.append(mode)

        # Save starting time
        self.start_time = datetime.datetime.now()

        # Launch worker
        self.logger.debug(f"launching process as : {arg_list}")
        self.process = subprocess.Popen(arg_list)

    def shutdown(self, grace_time=10) -> bool:
        """
        Tru to stop within <gracetime> seconds the current processus/worker
        :param grace_time: maximum waiting time
        :return: True if stopped, False otherwise
        """
        self.logger.info(f"Trying to stop (terminate) {self.process}")
        try:
            self.process.terminate()
            time.sleep(0.2)
        finally:
            try:
                self.process.wait(timeout=grace_time)
            except subprocess.TimeoutExpired:
                self.logger.info(f"Processus {self.process} did not terminate in time. Trying to kill it.")
            finally:
                try:
                    self.process.kill()
                    self.logger.info(f"Processus exited with {self.process.returncode}")
                    return True
                except subprocess.TimeoutExpired:
                    self.logger.info(f"Processus {self.process} is still alive .. Don't know how to stop it.")
                    return False

    def is_running(self) -> bool:
        """
        Check if current processus is running
        :return: True if process running, False otherwise
        """

        if self.process.poll() is None:
            return True
        return False

    def check_status(self, id_to_display):
        """
        Check and display status on logging output
        :param id_to_display: # of the worker, if you want to print one
        :return: True if process running, False otherwise
        """

        curr_str = f"==> Worker {id_to_display} : Launched on {self}"

        is_running = self.is_running()
        if is_running:
            curr_str += " status : running ..."
        else:
            curr_str += " status : terminated or ended ..."

        self.logger.info(curr_str)
        return is_running

    def wait_until_stopped(self, timeout: int = 60) -> bool:
        """
        Wait until the worker is stopped (= terminated)
        Put timeout -1 if you don't want to function to timeout
        :param timeout: maximal waiting time for the process to stop
        :return: True if stopped, False otherwise
        """

        start = time.time()

        while self.is_running():
            time.sleep(5)
            if timeout != -1 and abs(time.time() - start) > timeout:
                self.logger.warning("Waiting for worker to stop has timeout-ed.")
                return False

        self.logger.debug(f"Worker stopped after {round(abs(time.time() - start), 3)}s.")
        return True

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' processus=', self.process,
                                 ' worker_path=', str(self.worker_path),
                                 ' start_time=', self.start_time]))
