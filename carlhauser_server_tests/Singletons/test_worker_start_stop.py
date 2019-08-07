# -*- coding: utf-8 -*-

import logging
import pathlib
import unittest

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_adder as database_adder
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
from common.environment_variable import get_homedir


class testDistanceEngine(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_DistanceEngine/")

        # Create configurations
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()
        self.test_db_conf = test_database_only_conf.TestInstance_database_conf()

        print("[TESTS] LAUNCHING DATABASE AS TEST : NOTHING WILL BE WRITEN ON STORAGE OR CACHE DATABASES [TESTS]")
        # self.test_db_handler = test_database_handler.TestDatabaseHandler()
        # self.test_db_handler.setUp(db_conf=test_configuration)

        # Extract what we need : a distance engine
        self.db_adder = database_adder.Database_Adder(self.test_db_conf, self.dist_conf, self.fe_conf)
        self.distance_engine = distance_engine.Distance_Engine(self.db_adder, self.test_db_conf, self.dist_conf, self.fe_conf)

    '''

    def set_decode_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=True)
        self.distance_engine.storage_db = test_db
        self.db_adder.storage_db = test_db

    def set_raw_redis(self):
        test_db = redis.Redis(unix_socket_path=self.db_handler.get_socket_path('test'), decode_responses=False)
        self.distance_engine.storage_db = test_db
        self.db_adder.storage_db = test_db
    
    '''

    # ==================== ------ CLUSTER LIST ------- ====================

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
