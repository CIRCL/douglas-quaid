# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat

from carlhauser_server.Helpers.environment_variable import get_homedir

from carlhauser_client.API.extended_api import Extended_API, update_values_dict
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
from common.Graph.metadata import Metadata, Source


class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_client_tests/test_Helpers/id_generator")
        self.extended_api = Extended_API.get_api()

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_dict_update(self):
        ori_dict = {"test": "toto"}

        self.logger.info(f"Original dict : {pformat(ori_dict)}")
        res = self.extended_api.revert_mapping(ori_dict)
        self.logger.info(f"Reverted dict : {pformat(res)}")

        self.assertDictEqual(res, {'toto': 'test'})

    def test_dict_reverse(self):
        ori_dict = {"test": "toto", "aaa": "ddddd", "bbbb": "old"}
        futu_dict = {}
        old_value = "old"
        new_value = "new"

        self.logger.info(f"Original dict : \n{pformat(ori_dict)}")
        res = update_values_dict(ori_dict, futu_dict, {old_value:new_value})
        self.logger.info(f"Replaced dict : \n{pformat(res)}")

        self.assertDictEqual(res, {'test': 'toto', 'aaa': 'ddddd', 'bbbb': 'new'})

    def test_dict_reverse_hard(self):
        ori_dict = {"test": "toto",
                    "aaa": "ddddd",
                    "bbbb": "old",
                    "mylist": [
                        "test", "toto", "value", "old", "notold"
                    ],
                    "mysecondlist":
                        [
                            "minidict1"]
                    }
        futu_dict = {}
        old_value = "old"
        new_value = "new"

        self.logger.info(f"Original dict : \n{pformat(ori_dict)}")
        res = update_values_dict(ori_dict, futu_dict, {old_value:new_value})
        self.logger.info(f"Replaced dict : \n{pformat(res)}")
        self.assertDictEqual(res, {'aaa': 'ddddd',
                                   'bbbb': 'new',
                                   'mylist': ['test', 'toto', 'value', 'new', 'notold'],
                                   'mysecondlist': ['minidict1'],
                                   'test': 'toto'})

    def test_dict_reverse_realist(self):
        ori_dict = {
            "list_cluster": [
                {
                    "cluster_id": "cluster|fa7c7ff4-e831-4acd-8b39-f48ad9ff6aeb",
                    "distance": 0.17232142857142857
                },
                {
                    "cluster_id": "cluster|1627daed-2c7a-4965-a706-75e480b91842",
                    "distance": 0.2330357142857143
                },
                {
                    "cluster_id": "cluster|old",
                    "distance": 0.2580357142857143
                }
            ],
            "list_pictures": [
                {
                    "cluster_id": "cluster|fa7c7ff4-e831-4acd-8b39-f48ad9ff6aeb",
                    "distance": 0.0,
                    "image_id": "old"
                },
            ]}
        futu_dict = {}
        old_value = "old"
        new_value = "new"

        self.logger.info(f"Original dict : \n{pformat(ori_dict)}")
        res = update_values_dict(ori_dict, futu_dict, {old_value:new_value})
        self.logger.info(f"Replaced dict : \n{pformat(res)}")

        self.assertDictEqual(res, {'list_cluster': [{'cluster_id': 'cluster|fa7c7ff4-e831-4acd-8b39-f48ad9ff6aeb',
                                                     'distance': 0.17232142857142857},
                                                    {'cluster_id': 'cluster|1627daed-2c7a-4965-a706-75e480b91842',
                                                     'distance': 0.2330357142857143},
                                                    {'cluster_id': 'cluster|old',
                                                     'distance': 0.2580357142857143}],
                                   'list_pictures': [{'cluster_id': 'cluster|fa7c7ff4-e831-4acd-8b39-f48ad9ff6aeb',
                                                      'distance': 0.0,
                                                      'image_id': 'new'}]})


if __name__ == '__main__':
    unittest.main()
