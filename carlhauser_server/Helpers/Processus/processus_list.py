#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import subprocess
import sys
import time
from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

import carlhauser_server.Helpers.Processus.worker_processus as worker_processus


# ==================== ------ PATHS ------- ====================

class ProcessusList:
    def __init__(self, list_name: str, processus_list: List[worker_processus.WorkerProcessus]):
        self.list_name = list_name
        self.processus_list = processus_list
        self.logger = logging.getLogger(__name__)

    def flush_all_processus(self):
        # Kill each worker and then empty lists. Very violent.
        self.kill_all_processus()
        self.processus_list.clear()

    def kill_all_processus(self, grace_time=2):
        # Try to kill all workers of the given list, waiting <grace_time> for each processus to finish (2 sec per default)

        for proc in self.processus_list:
            self.logger.info(f"Trying to stop {proc.processus}")
            try:
                proc.processus.terminate()
                time.sleep(0.2)
            finally:
                try:
                    proc.processus.wait(timeout=grace_time)
                    self.logger.info(f"Processus exited with {proc.processus.returncode}")
                except subprocess.TimeoutExpired:
                    self.logger.info(f"Processus {proc.processus} did not terminate in time. Trying to kill it.")
                finally:
                    try:
                        proc.processus.kill()
                        self.logger.info(f"Processus exited with {proc.processus.returncode}")
                    except subprocess.TimeoutExpired:
                        self.logger.info(f"Processus {proc.processus} is still alive .. Don't know how to stop it.")

    def get_running_processus(self):
        # Provide a sublist of the list of processus, which are currently running
        running_workers = []

        for worker in self.processus_list:
            if worker.is_running():
                # All running workers are there
                running_workers.append(worker)

        return running_workers
