# -*- coding: utf-8 -*-

import logging
import unittest

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_server.API.API_server import FlaskAppWrapper
from carlhauser_server.Configuration.webservice_conf import Default_webservice_conf


class TestInMemoryOperations(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()

        # Create configurations
        self.db_conf = test_database_only_conf.TestInstance_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()
        self.ws_conf = Default_webservice_conf()

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.db_conf,
                                                  dist_conf=self.dist_conf,
                                                  fe_conf=self.fe_conf)

        self.api = Extended_API.get_api()

        self.flask = FlaskAppWrapper('api', tmp_ws_conf=self.ws_conf, tmp_db_conf=self.db_conf)
        self.flask.add_all_endpoints()

    def tearDown(self):
        # Launch shutdown AND FLUSH script
        self.test_db_handler.tearDown()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    #TODO : Handle context

if __name__ == '__main__':
    unittest.main()
