# -*- coding: utf-8 -*-

import subprocess
import time
import unittest
import cv2
import pathlib

import redis
import logging

from carlhauser_server.Helpers.environment_variable import get_homedir
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.Helpers.database_start_stop as database_start_stop
import carlhauser_server.DatabaseAccessor.database_adder as database_adder


class testDistanceEngine(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_DistanceEngine/")

        # Create configurations
        self.db_conf = database_conf.Default_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(conf=self.db_conf)

        # Scripts overwrite
        self.db_handler.test_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH / 'test.sock'
        self.db_handler.launch_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "run_redis_test.sh"
        self.db_handler.shutdown_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "shutdown_redis_test.sh"

        # Construct a worker and overwrite link to redis db
        self.db_adder = database_adder.Database_Adder(self.db_conf, self.dist_conf, self.fe_conf)
        self.db_adder.db_utils.db_access_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.db_adder.db_utils.db_access_no_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.db_adder.storage_db_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.db_adder.storage_db_no_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.de = distance_engine.Distance_Engine(self.db_adder, self.db_conf, self.dist_conf, self.fe_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.de.storage_db = test_db
        self.db_adder.storage_db = test_db

        # Launch test Redis DB
        if not self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.launch_test_script_path)], cwd=self.db_handler.launch_test_script_path.parent)

        # Time for the socket to be opened
        time.sleep(1)

    def set_decode_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.de.storage_db = test_db
        self.db_adder.storage_db = test_db

    def set_raw_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.de.storage_db = test_db
        self.db_adder.storage_db = test_db

    def tearDown(self):
        # Shutdown test Redis DB
        if self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.shutdown_test_script_path)], cwd=self.db_handler.test_socket_path.parent)

        # If start and stop are too fast, then it can't stop nor start, as it can't connect
        # e.g. because the new socket couldn't be create as the last one is still here
        time.sleep(1)

        # TODO : Kill subprocess ?

    # ==================== ------ CLUSTER LIST ------- ====================




    def test_absolute_truth_and_meaning(self):
        assert True


if __name__ == '__main__':
    unittest.main()
