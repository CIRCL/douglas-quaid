#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import pathlib
import time
import unittest

import cv2
import redis

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DatabaseAccessor.database_adder as database_adder
import carlhauser_server.DistanceEngine.distance_engine as distance_engine
import carlhauser_server.FeatureExtractor.picture_hasher as picture_hasher
import carlhauser_server.FeatureExtractor.picture_orber as picture_orber
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler
from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.environment_variable import QueueNames
from common.environment_variable import get_homedir
from carlhauser_server.DatabaseAccessor.database_utilities import DBUtilities


class testDBAdder(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_DistanceEngine/")

        # Create configurations
        self.test_db_conf = test_database_only_conf.TestInstance_database_conf()
        self.dist_conf = distance_engine_conf.Default_distance_engine_conf()
        self.fe_conf = feature_extractor_conf.Default_feature_extractor_conf()

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        self.test_db_handler.create_full_instance(db_conf=self.test_db_conf, dist_conf=self.dist_conf, fe_conf=self.fe_conf)

        db_access_no_decode = redis.Redis(unix_socket_path=self.test_db_handler.db_handler.get_socket_path('test'), decode_responses=False)
        db_access_decode = redis.Redis(unix_socket_path=self.test_db_handler.db_handler.get_socket_path('test'), decode_responses=True)
        self.db_utils = DBUtilities(db_access_decode=db_access_decode, db_access_no_decode=db_access_no_decode)

    def tearDown(self):
        # Launch shutdown AND FLUSH script
        self.test_db_handler.tearDown()

    def test_get_nb_stored_pictures(self):
        cluster_id = self.db_utils.add_picture_to_new_cluster("pic_1", 100)
        self.db_utils.add_picture_to_cluster("pic_2", cluster_id, 100)
        self.db_utils.add_picture_to_cluster("pic_3", cluster_id, 100)
        self.db_utils.add_picture_to_cluster("pic_4", cluster_id, 100)

        nb = self.db_utils.get_nb_stored_pictures()
        self.assertEqual(nb, 4)

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
