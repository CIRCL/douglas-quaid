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
import carlhauser_server.Processus.worker_processus as worker_processus

sys.path.append(os.path.abspath(os.path.pardir))

# ==================== ------ PATHS ------- ====================

class ProcessusList:
    # Handle a list of processus of one type

    def __init__(self, list_name: str, processus_list: List[worker_processus.WorkerProcessus]):
        self.list_name = list_name
        self.processus_list = processus_list
        self.logger = logging.getLogger(__name__)

    def append(self, process: worker_processus.WorkerProcessus):
        self.logger.debug(f"Adding worker : {process} to processes list {self.list_name}.")
        self.processus_list.append(process)

    def flush(self):
        self.processus_list.clear()

    def flush_not_running(self):
        # TODO
        pass

    def kill_all_processus(self, grace_time=2):
        # Try to kill all workers of the given list, waiting <grace_time> for each processus to finish (2 sec per default)

        for proc in self.processus_list:
            self.logger.info(f"Trying to stop {proc.process}")
            try:
                proc.process.terminate()
                time.sleep(0.2)
            finally:
                try:
                    proc.process.wait(timeout=grace_time)
                except subprocess.TimeoutExpired:
                    self.logger.info(f"Processus {proc.process} did not terminate in time. Trying to kill it.")
                finally:
                    try:
                        proc.process.kill()
                        self.logger.info(f"Processus exited with {proc.process.returncode}")
                    except subprocess.TimeoutExpired:
                        self.logger.info(f"Processus {proc.process} is still alive .. Don't know how to stop it.")

    def get_running_processus(self):
        # Provide a sublist of the list of processus, which are currently running
        running_workers = []

        for worker in self.processus_list:
            if worker.is_running():
                # All running workers are there
                running_workers.append(worker)

        return running_workers

    def is_there_alive_workers(self):
        # Check if workers are alive, and return True if all worker are down

        all_have_stopped = True
        self.logger.info(f"{len(self.processus_list)} worker(s) are presents in {self.list_name}.")

        for i, curr_proc in enumerate(self.processus_list):
            is_stopped = curr_proc.check_status(id_to_display=i)
            if not is_stopped:
                # If waiting has timeouted, return
                all_have_stopped = False
                break

        return all_have_stopped

    def wait_until_all_stopped(self, timeout: int = 60) -> bool:
        # Wait until all the workers are stopped (= terminated)
        # Put timeout -1 if you don't want to function to timeout

        all_have_stopped = True

        for i, curr_proc in enumerate(self.processus_list):
            self.logger.info(f"List {self.list_name} - waiting for worker {i} to stop ... ")
            are_stopped = curr_proc.wait_until_stopped(timeout=timeout)

            if not are_stopped:
                # If waiting has timeouted, return
                all_have_stopped = False
                break

        return all_have_stopped
