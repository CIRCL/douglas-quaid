#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys

# ==================== ------ PERSONAL LIBRARIES ------- ====================

from carlhauser_server.Helpers.template_singleton import Singleton
from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Helpers.socket as socket
import carlhauser_server.Configuration.database_conf as database_conf

sys.path.append(os.path.abspath(os.path.pardir))

# ==================== ------ PATHS ------- ====================

class Database_StartStop(object, metaclass=Singleton):
    # Singleton class that handle database access

    def __init__(self, db_conf: database_conf, handle_test_db: bool = False):
        # STD attributes
        self.db_conf = db_conf
        self.logger = logging.getLogger(__name__)
        self.logger.critical("SINGLETON CREATED (database start stop)")

        # Specific attributes
        self.socket_cache = socket.Socket(get_homedir() / self.db_conf.DB_SOCKETS_PATH_CACHE,
                                          get_homedir() / self.db_conf.DB_SCRIPTS_PATH_CACHE)
        self.socket_storage = socket.Socket(get_homedir() / self.db_conf.DB_SOCKETS_PATH_STORAGE,
                                            get_homedir() / self.db_conf.DB_SCRIPTS_PATH_STORAGE)

        self.handle_test_db = handle_test_db

        # if self.handle_test_db:
        self.socket_test = socket.Socket(get_homedir() / self.db_conf.DB_SOCKETS_PATH_TEST,
                                         get_homedir() / self.db_conf.DB_SCRIPTS_PATH_TEST)

    def get_socket_path(self, name: str) -> str:
        # Redis is configured to allow connection from/to Unix socket
        # Unix sockets paths for Redis are defined in cache.conf and storage.conf
        mapping = {
            'cache': self.socket_cache.socket_path,
            'storage': self.socket_storage.socket_path,
            'test': self.socket_test.socket_path,
        }
        return str(mapping[name])

    # ==================== ------ CACHE AND STORAGE MNGT ------- ====================

    def launch_all_redis(self):
        # Launch the cache, storage and test instance of redis
        self.socket_cache.launch()
        self.socket_storage.launch()
        if self.handle_test_db:
            self.socket_test.launch()

    def stop_all_redis(self):
        self.socket_cache.shutdown()
        self.socket_storage.shutdown()
        if self.handle_test_db:
            self.socket_test.shutdown()

    def flush_all_redis(self):
        self.socket_cache.flush()
        self.socket_storage.flush()
        if self.handle_test_db:
            self.socket_test.flush()

    def wait_until_all_redis_running(self):
        # Wait until all databases are launched and return True if all are running
        c_is_launched = self.socket_cache.wait_until_running()
        s_is_launched = self.socket_storage.wait_until_running()

        # Launch test DB if asked
        t_is_launched = True
        if self.handle_test_db:
            t_is_launched = self.socket_test.wait_until_running()

        # Create the boolean value
        if not c_is_launched or not s_is_launched or not t_is_launched:
            return False

        return True

    def wait_until_all_redis_stopped(self):
        self.socket_cache.wait_until_stopped()
        self.socket_storage.wait_until_stopped()
        if self.handle_test_db:
            self.socket_test.wait_until_stopped()

    def request_workers_shutdown(self):
        # Post a HALT key in all redis instance. Worker should react "quickly" and stop themselves
        self.socket_cache.stop_workers()
        self.socket_storage.stop_workers()
        if self.handle_test_db:
            self.socket_test.stop_workers()

    # ==================== ------ CACHE MNGT ------- ====================
    '''
    def launch_cache(self):
        # Launch cache instance of redis. Uses a launch script
        if not self.socket_cache.is_running():
            # subprocess.Popen([str(self.launch_cache_script_path)], cwd=self.launch_cache_script_path.parent)
            self.socket_cache.launch()

    def shutdown_cache(self):
        subprocess.Popen([str(self.shutdown_cache_script_path)], cwd=self.shutdown_cache_script_path.parent)

    def flush_cache(self):
        subprocess.Popen([str(self.flush_cache_script_path)], cwd=self.flush_cache_script_path.parent)

    '''

    # ==================== ------ STORAGE MNGT ------- ====================

    '''
    def launch_storage(self):
        # Launch storage instance of redis. Uses a launch script
        if not self.is_running('storage'):
            subprocess.Popen([str(self.launch_storage_script_path)], cwd=self.launch_storage_script_path.parent)

    def shutdown_storage(self):
        subprocess.Popen([self.shutdown_storage_script_path], cwd=self.shutdown_storage_script_path.parent)

    def flush_storage(self):
        subprocess.Popen([self.flush_storage_script_path], cwd=self.flush_storage_script_path.parent)

    '''

    # ==================== ------ CACHE AND STORAGE CHECKS ------- ====================
    '''
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
    
    '''

    '''
    # Specific attributes
    self.cache_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH_CACHE
    self.storage_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH_STORAGE
    self.test_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH_TEST

    # Cache scripts
    self.launch_cache_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_CACHE / "run.sh"
    self.shutdown_cache_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_CACHE / "shutdown.sh"
    self.flush_cache_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_CACHE / "flush.sh"

    # Storage scripts
    self.launch_storage_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_STORAGE / "run.sh"
    self.shutdown_storage_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_STORAGE / "shutdown.sh"
    self.flush_storage_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_STORAGE / "flush.sh"

    # Test scripts
    # self.launch_storage_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_TEST / "run.sh"
    # self.shutdown_storage_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_TEST / "shutdown.sh"
    # self.flush_storage_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH_TEST / "flush.sh"
    '''
