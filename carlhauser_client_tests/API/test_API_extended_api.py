# -*- coding: utf-8 -*-


import logging
import unittest
from pprint import pformat
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
from carlhauser_client.API.extended_api import Extended_API
from common.environment_variable import get_homedir

class TestAPIExtendedAPI(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_path = get_homedir() / "carlhauser_client_tests" / "API" / "ExtendedAPI"

        # Create configurations
        self.db_conf = test_database_only_conf.TestInstance_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.db_conf, dist_conf=self.dist_conf, fe_conf=self.fe_conf)

        self.api = Extended_API.get_api()

    def tearDown(self):
        # Launch shutdown AND FLUSH script
        self.test_db_handler.tearDown()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_add_one_picture_and_wait(self):
        img_id = self.api.add_one_picture_and_wait(self.test_path / "image.png")


    ''' 
    # TODO !
    def test_get_api(self):
        pass

    def test_add_pictures_to_db(self):
        pass

    def test_request_similar_and_wait(self):
        pass

    def test_request_pictures(self):
        pass
        
    def test_get_db_dump_as_graph(self):
        pass

    '''

if __name__ == '__main__':
    unittest.main()
