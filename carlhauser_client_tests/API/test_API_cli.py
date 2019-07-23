# -*- coding: utf-8 -*-

import logging
import unittest
from pprint import pformat
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
from carlhauser_client.API.simple_api import Simple_API
from common.environment_variable import get_homedir

class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_path = get_homedir() / "carlhauser_client_tests" / "API" / "API_pictures"

        # Create configurations
        self.db_conf = test_database_only_conf.TestInstance_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.db_conf, dist_conf=self.dist_conf, fe_conf=self.fe_conf)

        self.api = Simple_API.get_api()

    def tearDown(self):
        # Launch shutdown AND FLUSH script
        self.test_db_handler.tearDown()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
