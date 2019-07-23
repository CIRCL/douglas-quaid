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

    def test_ping_server_get(self):
        r = self.api.ping_server_get()
        self.assertEqual(r.status_code, 200)

    def test_ping_server_post(self):
        r = self.api.ping_server_post()
        self.assertEqual(r.status_code, 200)

    def test_ping_server(self):
        r = self.api.ping_server()
        self.assertEqual(r, True)

    def test_add_one_picture(self):
        r = self.api.add_one_picture(self.test_path / "image.png")
        self.assertEqual(r[0], True)
        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.assertEqual(r[1], "8114519b-044f-5800-9a81-2fc5f6a20220")

    def test_poll_until_adding_done(self):
        pic_id = self.api.add_one_picture(self.test_path / "image.png")

        # Timeout of 0 = Should return immediately with False
        r = self.api.poll_until_adding_done(0)
        self.assertEqual(r, False)

        # Timeout of (infinite) should return True, as the picture will be added one day
        r = self.api.poll_until_adding_done(-1)
        self.assertEqual(r, True)

    def test_is_adding_done(self):
        pic_id = self.api.add_one_picture(self.test_path / "image.png")

        # Timeout of 0 = Should return immediately with False
        r = self.api.is_adding_done()
        self.assertEqual(r[0], True)
        self.assertEqual(r[1], False)

        r = self.api.poll_until_adding_done(-1)
        self.assertEqual(r, True)

        # Timeout of 0 = Should return immediately with False
        r = self.api.is_adding_done()
        self.assertEqual(r[0], True)
        self.assertEqual(r[1], True)

    def test_request_similar(self):
        success, request_id = self.api.request_similar(self.test_path / "image.jpg")
        self.assertEqual(success, True)
        self.logger.info("Request made")

    def test_poll_until_result_ready(self):
        pic_id_yes = self.api.add_one_picture(self.test_path / "image.png")
        pic_id_no = self.api.add_one_picture(self.test_path / "very_different.png")
        self.logger.info("Added pictures")

        r = self.api.poll_until_adding_done(-1)
        self.assertEqual(r, True)

        success, request_id = self.api.request_similar(self.test_path / "image.jpg")
        self.assertEqual(success, True)
        self.logger.info("Request made")

        r = self.api.poll_until_result_ready(request_id, 0)
        self.assertEqual(r, False)

        r = self.api.poll_until_result_ready(request_id, -1)
        self.assertEqual(r, True)

    def test_get_results(self):
        success, pic_id_yes = self.api.add_one_picture(self.test_path / "image.png")
        success, pic_id_no = self.api.add_one_picture(self.test_path / "very_different.png")
        self.logger.info("Added pictures")

        r = self.api.poll_until_adding_done(-1)
        self.assertEqual(r, True)

        success, request_id = self.api.request_similar(self.test_path / "image.jpg")
        self.assertEqual(success, True)
        self.logger.info("Request made")

        r = self.api.poll_until_result_ready(request_id, 0)
        self.assertEqual(r, False)

        r = self.api.poll_until_result_ready(request_id, -1)
        self.assertEqual(r, True)

        success, results = self.api.get_results(request_id)
        self.assertEqual(success, True)
        self.logger.info("Result fetched")
        self.logger.info(pformat(results))

        awaited_result = [{'cluster_id': 'cluster|28bd1119-fc64-451d-b489-dc69f3a4d18c',
                    'decision': 'YES',
                    'distance': 0.031919642857142855,
                    'image_id': '8114519b-044f-5800-9a81-2fc5f6a20220'},
                   {'cluster_id': 'cluster|06759547-d359-4aac-b6a7-f537d778c754',
                    'decision': 'MAYBE',
                    'distance': 0.3788783482142857,
                    'image_id': 'ce75e7ba-eb4d-5421-a80c-326cce54afd1'}]

        self.assertEqual(results["list_pictures"][0]["image_id"], pic_id_yes)
        self.assertEqual(results["list_pictures"][0]["decision"], "YES")
        self.assertEqual(results["list_pictures"][1]["image_id"], pic_id_no)
        self.assertNotEqual(results["list_pictures"][1]["decision"], "YES")

    def test_is_result_ready(self):
        pic_id_yes = self.api.add_one_picture(self.test_path / "image.png")
        pic_id_no = self.api.add_one_picture(self.test_path / "very_different.png")
        self.logger.info("Added pictures")

        r = self.api.poll_until_adding_done(-1)
        self.assertEqual(r, True)

        success, request_id = self.api.request_similar(self.test_path / "image.jpg")
        self.assertEqual(success, True)
        self.logger.info("Request made")

        success, ready = self.api.is_result_ready(request_id)
        self.assertEqual(success, False)
        self.assertEqual(ready, False)

        r = self.api.poll_until_result_ready(request_id, -1)
        self.assertEqual(r, True)

        success, ready = self.api.is_result_ready(request_id)
        self.assertEqual(success, True)
        self.assertEqual(ready, True)

    def test_export_db_server(self):
        pic_id_yes = self.api.add_one_picture(self.test_path / "image.png")
        pic_id_no = self.api.add_one_picture(self.test_path / "very_different.png")
        self.logger.info("Added pictures")

        r = self.api.poll_until_adding_done(-1)
        self.assertEqual(r, True)

        success, db = self.api.export_db_server()
        self.assertEqual(success, True)
        self.logger.info("db fetched")
        self.logger.info(pformat(db))

        self.assertEqual(len(db["nodes"]), 2)
        self.assertEqual(len(db["edges"]), 2)

        '''
        {'clusters': [{'group': '',
               'id': 'cluster|b4d3ac7c-1c83-4b58-b4ec-04b84275735f',
               'image': '',
               'label': '',
               'members': ['8114519b-044f-5800-9a81-2fc5f6a20220'],
               'shape': 'image'},
              {'group': '',
               'id': 'cluster|2f604b65-ca67-4e34-8a80-23585db15f91',
               'image': '',
               'label': '',
               'members': ['ce75e7ba-eb4d-5421-a80c-326cce54afd1'],
               'shape': 'image'}],
 'edges': [{'color': 'gray',
            'from': 'cluster|b4d3ac7c-1c83-4b58-b4ec-04b84275735f',
            'to': '8114519b-044f-5800-9a81-2fc5f6a20220'},
           {'color': 'gray',
            'from': 'cluster|2f604b65-ca67-4e34-8a80-23585db15f91',
            'to': 'ce75e7ba-eb4d-5421-a80c-326cce54afd1'}],
 'meta': {'source': 'DBDUMP'},
 'nodes': [{'id': '8114519b-044f-5800-9a81-2fc5f6a20220',
            'image': '',
            'label': 0.0,
            'shape': 'image'},
           {'id': 'ce75e7ba-eb4d-5421-a80c-326cce54afd1',
            'image': '',
            'label': 0.0,
            'shape': 'image'}]}
        '''


if __name__ == '__main__':
    unittest.main()
