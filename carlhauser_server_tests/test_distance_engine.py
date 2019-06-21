# -*- coding: utf-8 -*-

import subprocess
import time
import unittest

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
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/environment_variable")

        self.db_conf = database_conf.Default_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        # Create database handler from configuration file
        self.db_handler = database_start_stop.Database_StartStop(conf=self.db_conf)

        # Test data
        self.db_handler.test_socket_path = get_homedir() / self.db_conf.DB_SOCKETS_PATH / 'test.sock'
        self.db_handler.launch_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "run_redis_test.sh"
        self.db_handler.shutdown_test_script_path = get_homedir() / self.db_conf.DB_SCRIPTS_PATH / "shutdown_redis_test.sh"

        # Construct a worker and get a link to redis db
        self.db_adder = database_adder.Database_Adder(self.db_conf, self.dist_conf, self.fe_conf)
        self.db_adder.storage_db_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.db_adder.storage_db_no_decode = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.de = distance_engine.Distance_Engine(self.db_adder, self.db_conf, self.dist_conf, self.fe_conf)
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)

        self.de.storage_db = test_db

        # Launch test Redis DB
        if not self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.launch_test_script_path)], cwd=self.db_handler.launch_test_script_path.parent)

        # Time for the socket to be opened
        time.sleep(1)

    def tearDown(self):
        # Shutdown test Redis DB
        if self.db_handler.is_running('test'):
            subprocess.Popen([str(self.db_handler.shutdown_test_script_path)], cwd=self.db_handler.test_socket_path.parent)

        # If start and stop are too fast, then it can't stop nor start, as it can't connect
        # e.g. because the new socket couldn't be create as the last one is still here
        time.sleep(1)

        # TODO : Kill subprocess ?


    '''
        def test_get_top_matching_clusters(self):
        id_to_process = str(42)
        data_to_store = {"P-HASH":"0000000111100","ORB":"orb_desriptors_list"}
        #TODO : Make better example

        # Add picture to storage
        list_clusters = self.ce.get_top_matching_clusters(data_to_store)

        # Checks
        self.assertEqual([0,1,2],list_clusters)
    '''


    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
