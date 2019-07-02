#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import os
import subprocess
import sys
import pathlib
import datetime
import time
import logging

# ==================== ------ PERSONAL LIBRARIES ------- ====================

from common.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf

import common.ImportExport.json_import_export as json_import_export
sys.path.append(os.path.abspath(os.path.pardir))


# ==================== ------ PATHS ------- ====================

# Small class to handle processus
class WorkerProcessus:
    def __init__(self, worker_path: pathlib.Path):
        self.worker_path = worker_path
        self.process = None  # processus: subprocess.Popen
        self.start_time = None

        self.logger = logging.getLogger(__name__)

    def launch(self, db_conf: database_conf = None, dist_conf: distance_engine_conf = None, fe_conf: feature_extractor_conf = None, ws_conf: webservice_conf = None, mode=None):
        # Construct an argument list to be 'popen' as a new process
        arg_list = [str(self.worker_path)]

        # Save current configuration in files
        # Using self.worker_path.parent
        if db_conf is not None:
            tmp_db_conf_path =  get_homedir() / "tmp_db_conf.json"
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

        # Save starting time
        self.start_time = datetime.datetime.now()

        # Launch worker
        self.logger.debug(f"launching process as : {arg_list}")
        self.process = subprocess.Popen(arg_list)

    def shutdown(self, grace_time=10):
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
                except subprocess.TimeoutExpired:
                    self.logger.info(f"Processus {self.process} is still alive .. Don't know how to stop it.")

    def is_running(self):
        # Check if current processus is running
        if self.process.poll() is None:
            return True
        return False

    def check_status(self, id_to_display):
        # Display and check status
        curr_str = f"==> Worker {id_to_display} : Launched on {self}"

        is_running = self.is_running()
        if is_running:
            curr_str += " status : running ..."
        else:
            curr_str += " status : terminated or ended ..."

        self.logger.info(curr_str)
        return is_running

    def wait_until_stopped(self, timeout: int = 60) -> bool:
        # Wait until the worker is stopped (= terminated)
        # Put timeout -1 if you don't want to function to timeout

        start = time.time()

        while self.is_running():
            time.sleep(5)
            if timeout != -1 and abs(time.time() - start) > timeout:
                self.logger.warning("Waiting for worker to stop has timeout-ed.")
                return False

        return True

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' processus=', self.process, ' worker_path=', str(self.worker_path), ' start_time=', self.start_time]))
