#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Helpers.socket as socket
from carlhauser_server.Singletons.singleton import Singleton
from common.environment_variable import get_homedir
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class Database_StartStop(object, metaclass=Singleton):
    """
    Singleton class that handle database access
    """

    def __init__(self, db_conf: database_conf.Default_database_conf):
        # STD attributes
        self.db_conf = db_conf
        self.logger = logging.getLogger(__name__)
        self.logger.critical("SINGLETON CREATED (database start stop)")
        self.logger.debug(f"Only the test database will be used = {self.db_conf.ONLY_TEST_DB}")

        # Specific attributes
        # We are in a test mode, so we want the test database to be handled too.
        if self.db_conf.ONLY_TEST_DB:
            self.socket_test = socket.Socket(get_homedir() / self.db_conf.DB_SOCKETS_PATH_TEST,
                                             get_homedir() / self.db_conf.DB_SCRIPTS_PATH_TEST)
            self.mapping = {
                'cache': self.socket_test.socket_path,
                'storage': self.socket_test.socket_path,
                'test': self.socket_test.socket_path,
            }
        else:
            self.socket_cache = socket.Socket(get_homedir() / self.db_conf.DB_SOCKETS_PATH_CACHE,
                                              get_homedir() / self.db_conf.DB_SCRIPTS_PATH_CACHE)
            self.socket_storage = socket.Socket(get_homedir() / self.db_conf.DB_SOCKETS_PATH_STORAGE,
                                                get_homedir() / self.db_conf.DB_SCRIPTS_PATH_STORAGE)
            self.mapping = {
                'cache': self.socket_cache.socket_path,
                'storage': self.socket_storage.socket_path,
            }

    def get_socket_path(self, name: str) -> str:
        """
        Redis is configured to allow connection from/to Unix socket
        Unix sockets paths for Redis are defined in cache.conf and storage.conf
        :param name: The name of the socket Type to get
        :return: The socket object
        """
        return str(self.mapping[name])

    # ==================== ------ CACHE AND STORAGE MNGT ------- ====================

    def launch_all_redis(self):
        """
        Launch the cache, storage and test instance of redis
        :return: Nothing
        """

        if self.db_conf.ONLY_TEST_DB:
            self.socket_test.launch()
        else:
            self.socket_cache.launch()
            self.socket_storage.launch()

    def stop_all_redis(self):
        """
        Stop the cache, storage and test instance of redis
        :return: Nothing
        """

        if self.db_conf.ONLY_TEST_DB:
            self.socket_test.shutdown()
        else:
            self.socket_cache.shutdown()
            self.socket_storage.shutdown()

    def flush_all_redis(self):
        """
        Flush the cache, storage and test instance of redis
        :return: Nothing
        """

        if self.db_conf.ONLY_TEST_DB:
            self.socket_test.flush()
        else:
            self.socket_cache.flush()
            self.socket_storage.flush()

    def wait_until_all_redis_running(self):
        """
        Blocking function that wait until all database are launched.
        :return: True if all are launched, False otherwise
        """

        # Launch test DB if asked
        t_is_launched = True
        c_is_launched = True
        s_is_launched = True

        # Wait until all databases are launched and return True if all are running
        if self.db_conf.ONLY_TEST_DB:
            t_is_launched = self.socket_test.wait_until_running()
        else:
            c_is_launched = self.socket_cache.wait_until_running()
            s_is_launched = self.socket_storage.wait_until_running()

        # Create the boolean value
        if not c_is_launched or not s_is_launched or not t_is_launched:
            return False

        return True

    def wait_until_all_redis_stopped(self):
        """
        Blocking function that wait until all database are stopped.
        :return: True if all are stopped, False otherwise
        """

        t_is_stopped = True
        c_is_stopped = True
        s_is_stopped = True

        # Wait until all databases are stopped and return True if all are stopped
        if self.db_conf.ONLY_TEST_DB:
            t_is_stopped = self.socket_test.wait_until_stopped()
        else:
            c_is_stopped = self.socket_cache.wait_until_stopped()
            s_is_stopped = self.socket_storage.wait_until_stopped()

        # Create the boolean value
        if not c_is_stopped or not s_is_stopped or not t_is_stopped:
            return False

        return True

    def prevent_workers_shutdown(self):
        """
        Remove HALT key in all redis instance. Worker then can't stop themselves on launch
        :return: Nothing
        """

        if self.db_conf.ONLY_TEST_DB:
            self.socket_test.prevent_workers_stop()
        else:
            self.socket_cache.prevent_workers_stop()
            self.socket_storage.prevent_workers_stop()

    def request_workers_shutdown(self):
        """
        Post a HALT key in all redis instance. Worker should react "quickly" and stop themselves
        :return: Nothing
        """

        if self.db_conf.ONLY_TEST_DB:
            self.socket_test.stop_workers()
        else:
            self.socket_cache.stop_workers()
            self.socket_storage.stop_workers()
