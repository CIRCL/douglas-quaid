#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import subprocess
import sys
import time

import redis

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.template_singleton import Singleton
from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf


# ==================== ------ PATHS ------- ====================

class Database_StartStop(object, metaclass=Singleton):
    # Singleton class that handle database access

    def __init__(self, conf: database_conf):
        # STD attributes
        self.conf = conf
        self.logger = logging.getLogger(__name__)

        # Specific attributes
        self.cache_socket_path = get_homedir() / self.conf.DB_SOCKETS_PATH / 'cache.sock'
        self.storage_socket_path = get_homedir() / self.conf.DB_SOCKETS_PATH / 'storage.sock'

        # Cache scripts
        self.launch_cache_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "run_redis_cache.sh"
        self.shutdown_cache_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "shutdown_redis_cache.sh"
        self.flush_cache_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "flush_redis_cache.sh"

        # Storage scripts
        self.launch_storage_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "run_redis_storage.sh"
        self.shutdown_storage_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "shutdown_redis_storage.sh"
        self.flush_storage_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "flush_redis_storage.sh"

        # Only for test purposes
        self.test_socket_path = get_homedir() / self.conf.DB_SOCKETS_PATH / 'test.sock'

    def get_socket_path(self, name: str) -> str:
        # Redis is configured to allow connection from/to Unix socket
        # Unix sockets paths for Redis are defined in cache.conf and storage.conf
        mapping = {
            'cache': self.cache_socket_path,
            'storage': self.storage_socket_path,
            'test': self.test_socket_path,
        }
        return str(mapping[name])

    # ==================== ------ CACHE MNGT ------- ====================

    def launch_cache(self):
        # Launch cache instance of redis. Uses a launch script
        if not self.is_running('cache'):
            subprocess.Popen([str(self.launch_cache_script_path)], cwd=self.launch_cache_script_path.parent)

    def shutdown_cache(self):
        subprocess.Popen([str(self.shutdown_cache_script_path)], cwd=self.shutdown_cache_script_path.parent)

    def flush_cache(self):
        subprocess.Popen([str(self.flush_cache_script_path)], cwd=self.flush_cache_script_path.parent)

    # ==================== ------ STORAGE MNGT ------- ====================

    def launch_storage(self):
        # Launch storage instance of redis. Uses a launch script
        if not self.is_running('storage'):
            subprocess.Popen([str(self.launch_storage_script_path)], cwd=self.launch_storage_script_path.parent)

    def shutdown_storage(self):
        subprocess.Popen([self.shutdown_storage_script_path], cwd=self.shutdown_storage_script_path.parent)

    def flush_storage(self):
        subprocess.Popen([self.flush_storage_script_path], cwd=self.flush_storage_script_path.parent)

    # ==================== ------ CACHE AND STORAGE MNGT ------- ====================

    def launch_all_redis(self):
        # Launch the cache instance of redis, and the storage instance of redis
        self.launch_cache()
        self.launch_storage()

    def stop_all_redis(self):
        self.shutdown_cache()
        self.shutdown_storage()

    def flush_all_redis(self):
        self.flush_cache()
        self.flush_storage()

    # ==================== ------ CACHE AND STORAGE CHECKS ------- ====================

    def wait_until_running(self, name: str, timeout: int = 60) -> bool:
        # Wait until the database is launch (= answer to a ping)
        # Put timeout -1 if you don't want to function to timeout

        start = time.time()

        while not self.is_running(name):
            time.sleep(5)
            if timeout != -1 and abs(time.time() - start) > timeout:
                self.logger.warning("Waiting for Redis database to run timeouted.")
                return False

        return True

    def wait_until_stopped(self, name: str, timeout: int = 60) -> bool:
        # Wait until the database is stopped (= does not answer to a ping)
        # Put timeout -1 if you don't want to function to timeout

        start = time.time()

        while self.is_running(name):
            time.sleep(5)
            if timeout != -1 and abs(time.time() - start) > timeout:
                self.logger.warning("Waiting for Redis database to stop timeouted.")
                return False

        return True

    def is_running(self, name: str) -> bool:
        socket_path = self.get_socket_path(name)
        try:
            r = redis.Redis(unix_socket_path=socket_path)
            if r.ping():
                return True
        except Exception as e:
            # logger = logging.getLogger(__name__)
            # logger.error(f"PING got no answer. Invalid socket. {e}")
            return False

    def check_all_redis(self, stop=False):
        # TODO : Review usage ?
        # Ping cache socket and storage socket
        backends = [['cache', False], ['storage', False]]
        while True:
            for b in backends:
                try:
                    b[1] = self.is_running(b[0])
                except Exception:
                    b[1] = False
            if stop:
                if not any(b[1] for b in backends):
                    break
            else:
                if all(b[1] for b in backends):
                    break
            for b in backends:
                if not stop and not b[1]:
                    print(f"Waiting on {b[0]}")
                if stop and b[1]:
                    print(f"Waiting on {b[0]}")
            time.sleep(1)
