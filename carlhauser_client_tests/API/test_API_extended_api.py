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
from common.Graph.graph_datastructure import GraphDataStruct


class TestAPIExtendedAPI(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_path = get_homedir() / "datasets" / "douglas-quaid-tests" / "API_pictures"

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
        success, img_id = self.api.add_one_picture_and_wait(self.test_path / "image.png")
        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.assertEqual(img_id, "8114519b-044f-5800-9a81-2fc5f6a20220")

    def test_add_many_pictures_no_wait(self):
        mapping_filename_to_id, nb_pics_sent = self.api.add_many_pictures_no_wait(self.test_path)

        expected_mapping = {'image.bmp': '729f3e02-c138-5ccd-ad08-2b7f56206e1d',
                            'image.jpg': 'aab51a4c-cd7a-58c7-934a-7c00e9673d1e',
                            'image.png': '8114519b-044f-5800-9a81-2fc5f6a20220',
                            'very_different.png': 'ce75e7ba-eb4d-5421-a80c-326cce54afd1'}

        self.assertEqual(nb_pics_sent, 4)

        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Mapping fetched")
        self.logger.info(pformat(mapping_filename_to_id))
        self.assertDictEqual(expected_mapping, mapping_filename_to_id)

    def test_add_many_picture_and_wait_for_each(self):
        mapping_filename_to_id, nb_pics_sent = self.api.add_many_picture_and_wait_for_each(self.test_path)
        self.assertEqual(nb_pics_sent, 4)

        expected_mapping = {'image.bmp': '729f3e02-c138-5ccd-ad08-2b7f56206e1d',
                            'image.jpg': 'aab51a4c-cd7a-58c7-934a-7c00e9673d1e',
                            'image.png': '8114519b-044f-5800-9a81-2fc5f6a20220',
                            'very_different.png': 'ce75e7ba-eb4d-5421-a80c-326cce54afd1'}

        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Result fetched")
        self.logger.info(pformat(mapping_filename_to_id))
        self.assertDictEqual(expected_mapping, mapping_filename_to_id)

    def test_request_one_picture_and_wait(self):
        success, img_id = self.api.add_one_picture_and_wait(self.test_path / "image.png")
        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.assertEqual(img_id, "8114519b-044f-5800-9a81-2fc5f6a20220")

        results = self.api.request_one_picture_and_wait(self.test_path / "image.png")

        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Result fetched")
        self.logger.info(pformat(results))
        self.assertEqual(results["list_pictures"][0]["image_id"], '8114519b-044f-5800-9a81-2fc5f6a20220')

    def test_request_many_pictures_and_wait_for_each(self):
        mapping_filename_to_id, nb_pics_sent = self.api.add_many_picture_and_wait_for_each(self.test_path)
        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Mapping fetched")
        self.logger.info(pformat(mapping_filename_to_id))
        self.assertEqual(nb_pics_sent, 4)

        expected_mapping = {'image.bmp': '729f3e02-c138-5ccd-ad08-2b7f56206e1d',
                            'image.jpg': 'aab51a4c-cd7a-58c7-934a-7c00e9673d1e',
                            'image.png': '8114519b-044f-5800-9a81-2fc5f6a20220',
                            'very_different.png': 'ce75e7ba-eb4d-5421-a80c-326cce54afd1'}
        self.assertDictEqual(expected_mapping, mapping_filename_to_id)

        list_answers, nb_pics_requested = self.api.request_many_pictures_and_wait_for_each(self.test_path)

        self.assertEqual(len(list_answers), 4)

        # Do mapping
        tmp_dict = {}
        for i in list_answers:
            tmp_dict[i["request_id"]] = i

        self.assertEqual(tmp_dict["729f3e02-c138-5ccd-ad08-2b7f56206e1d"]["list_pictures"][0]["image_id"], '729f3e02-c138-5ccd-ad08-2b7f56206e1d')
        self.assertEqual(tmp_dict["aab51a4c-cd7a-58c7-934a-7c00e9673d1e"]["list_pictures"][0]["image_id"], 'aab51a4c-cd7a-58c7-934a-7c00e9673d1e')
        self.assertEqual(tmp_dict["ce75e7ba-eb4d-5421-a80c-326cce54afd1"]["list_pictures"][0]["image_id"], 'ce75e7ba-eb4d-5421-a80c-326cce54afd1')
        self.assertEqual(tmp_dict["8114519b-044f-5800-9a81-2fc5f6a20220"]["list_pictures"][0]["image_id"], '8114519b-044f-5800-9a81-2fc5f6a20220')

        self.assertEqual(nb_pics_requested, 4)
        '''
        [{'list_cluster': [(...)],
         'list_pictures': [{'cluster_id': 'cluster|5aff692c-d43c-4e62-923e-233d988be582',
                     'decision': 'YES',
                     'distance': 0.0,
                     'image_id': '729f3e02-c138-5ccd-ad08-2b7f56206e1d'},
                    {'cluster_id': 'cluster|5aff692c-d43c-4e62-923e-233d988be582',
                     'decision': 'YES',
                     'distance': 0.00703125,
                     'image_id': 'aab51a4c-cd7a-58c7-934a-7c00e9673d1e'}, (...)
  'request_id': '729f3e02-c138-5ccd-ad08-2b7f56206e1d',
  'request_time': 2.111865997314453,
  'status': 'matches_found'},
 {'list_cluster': [{(...)
        '''

        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Result fetched")
        self.logger.info(pformat(list_answers))

    def test_request_many_pictures_and_wait_global(self):
        mapping_filename_to_id, nb_pics_sent = self.api.add_many_picture_and_wait_for_each(self.test_path)
        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Mapping fetched")
        self.logger.info(pformat(mapping_filename_to_id))
        self.assertEqual(nb_pics_sent, 4)

        list_answers, nb_pics_requested = self.api.request_many_pictures_and_wait_global(self.test_path)

        self.assertEqual(nb_pics_requested, 4)

        # Do mapping
        print(pformat(list_answers))
        tmp_dict = {}
        for i in list_answers:
            print(i)
            try :
                tmp_dict[i["request_id"]] = i
            except Exception as e :
                self.logger.critical(f"Error during fetching request id in result list : {e}")

        self.assertEqual(tmp_dict["729f3e02-c138-5ccd-ad08-2b7f56206e1d"]["list_pictures"][0]["image_id"], '729f3e02-c138-5ccd-ad08-2b7f56206e1d')
        self.assertEqual(tmp_dict["aab51a4c-cd7a-58c7-934a-7c00e9673d1e"]["list_pictures"][0]["image_id"], 'aab51a4c-cd7a-58c7-934a-7c00e9673d1e')
        self.assertEqual(tmp_dict["ce75e7ba-eb4d-5421-a80c-326cce54afd1"]["list_pictures"][0]["image_id"], 'ce75e7ba-eb4d-5421-a80c-326cce54afd1')
        self.assertEqual(tmp_dict["8114519b-044f-5800-9a81-2fc5f6a20220"]["list_pictures"][0]["image_id"], '8114519b-044f-5800-9a81-2fc5f6a20220')
        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Result fetched")
        self.logger.info(pformat(list_answers))

    def test_get_db_dump_as_graph(self):
        mapping_filename_to_id, nb_pics_sent = self.api.add_many_picture_and_wait_for_each(self.test_path)
        # UUID v5 of SHA1 of the picture. Deterministic ;)
        self.logger.info("Mapping fetched")
        self.logger.info(pformat(mapping_filename_to_id))
        self.assertEqual(nb_pics_sent, 4)

        graph: GraphDataStruct = self.api.get_db_dump_as_graph()
        self.logger.info("Graph ")
        self.logger.info(pformat(graph.export_as_dict()))

        # TODO : Add graph test

    def test_add_and_request_and_dump_pictures(self):
        results_list = self.api.add_and_request_and_dump_pictures(self.test_path)

        self.logger.info("Result fetched")
        self.logger.info(pformat(results_list))

        # Do mapping
        tmp_dict = {}
        for i in results_list:
            print(i)
            tmp_dict[i["request_id"]] = i

        self.assertEqual(tmp_dict["image.bmp"]["list_pictures"][0]["image_id"], 'image.bmp')
        self.assertEqual(tmp_dict["image.jpg"]["list_pictures"][0]["image_id"], 'image.jpg')
        self.assertEqual(tmp_dict["image.png"]["list_pictures"][0]["image_id"], 'image.png')
        self.assertEqual(tmp_dict["very_different.png"]["list_pictures"][0]["image_id"], 'very_different.png')


if __name__ == '__main__':
    unittest.main()
