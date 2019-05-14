#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import subprocess
import pathlib
import time
import redis
import logging

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.template_singleton import Singleton
from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf


# ==================== ------ PATHS ------- ====================

class Database_StartStop(object, metaclass=Singleton):
    # Singleton class that handle database access
    _instance = None

    def __init__(self, conf: database_conf):
        # STD attributes
        self.conf = conf
        self.logger = logging.getLogger(__name__)

        # Specific attributes
        self.cache_socket_path = get_homedir() / self.conf.DB_SOCKETS_PATH / 'cache.sock'
        self.storage_socket_path = get_homedir() / self.conf.DB_SOCKETS_PATH / 'storage.sock'

        self.launch_cache_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "run_redis_cache.sh"
        self.shutdown_cache_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "shutdown_redis_cache.sh"
        self.launch_storage_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "run_redis_storage.sh"
        self.shutdown_storage_script_path = get_homedir() / self.conf.DB_SCRIPTS_PATH / "shutdown_redis_storage.sh"

    def get_socket_path(self, name: str) -> str:
        # Redis is configured to allow connection from/to Unix socket
        # Unix sockets paths for Redis are defined in cache.conf and storage.conf
        mapping = {
            'cache': self.cache_socket_path,
            'storage': self.storage_socket_path,
        }
        return str(mapping[name])

    def check_running(self, name: str) -> bool:
        socket_path = self.get_socket_path(name)
        try:
            r = redis.Redis(unix_socket_path=socket_path)
            if r.ping():
                return True
        except Exception as e:
            # logger = logging.getLogger(__name__)
            # logger.error(f"PING got no answer. Invalid socket. {e}")
            return False

    # ==================== ------ CACHE MNGT ------- ====================

    def launch_cache(self):
        # Launch cache instance of redis. Uses a launch script
        if not self.check_running('cache'):
            subprocess.Popen([str(self.launch_cache_script_path)], cwd=(self.launch_cache_script_path.parent))

    def shutdown_cache(self):
        subprocess.Popen([str(self.shutdown_cache_script_path)], cwd=(self.shutdown_cache_script_path.parent))

    # ==================== ------ STORAGE MNGT ------- ====================

    def launch_storage(self):
        # Launch storage instance of redis. Uses a launch script
        if not self.check_running('storage'):
            subprocess.Popen([str(self.launch_storage_script_path)], cwd=(self.launch_storage_script_path.parent))

    def shutdown_storage(self):
        subprocess.Popen([self.shutdown_storage_script_path], cwd=(self.shutdown_storage_script_path.parent))

    # ==================== ------ ALL MNGT ------- ====================

    def launch_all_redis(self):
        # Launch the cache instance of redis, and the storage instance of redis
        self.launch_cache()
        self.launch_storage()

    def check_all_redis(self, stop=False):
        # Ping cache socket and storage socket
        backends = [['cache', False], ['storage', False]]
        while True:
            for b in backends:
                try:
                    b[1] = self.check_running(b[0])
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

    def stop_all_redis(self):
        self.shutdown_cache()
        self.shutdown_storage()
