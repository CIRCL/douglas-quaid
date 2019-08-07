#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import unittest
from pprint import pformat

import redis

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_server.DatabaseAccessor.database_utilities import DBUtilities
from common.environment_variable import get_homedir


class testDBAdder(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        self.test_file_path = get_homedir() / "datasets" / "TEST_DATASETS" / "DBUtils"

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

    def test_get_nb_stored_pictures_a_lot(self):
        api = Extended_API.get_api()
        mapping, nb_pics_sent = api.add_many_pictures_and_wait_global(image_folder=self.test_file_path / "MINI_DATASET_DEDUPLICATED")

        nb = self.db_utils.get_nb_stored_pictures()

        self.logger.info(pformat(mapping))

        self.assertEqual(nb, nb_pics_sent)
        self.assertEqual(nb, 38)

    def test_get_nb_stored_pictures_a_lot_handle_duplicates(self):
        api = Extended_API.get_api()
        mapping, nb_pics_sent = api.add_many_pictures_and_wait_global(image_folder=self.test_file_path / "MINI_DATASET")

        nb = self.db_utils.get_nb_stored_pictures()

        self.logger.info(pformat(mapping))

        self.assertNotEqual(nb, nb_pics_sent)
        self.assertNotEqual(nb, 46)

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
