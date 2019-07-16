# -*- coding: utf-8 -*-

import logging
import unittest

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf


class testDistanceEngine(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/environment_variable")

        self.db_conf = database_conf.Default_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

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
