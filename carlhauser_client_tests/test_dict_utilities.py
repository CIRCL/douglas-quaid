# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat

from common.environment_variable import get_homedir

import carlhauser_client.EvaluationTools.StorageGraphExtractor.cluster_matcher as cluster_matcher
from common.Graph.cluster import Cluster


class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)


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
        res = update_values_dict(ori_dict, futu_dict, {old_value: new_value})
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
        res = update_values_dict(ori_dict, futu_dict, {old_value: new_value})
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
        res = update_values_dict(ori_dict, futu_dict, {old_value: new_value})
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


    ''' 
    # TODO !
    def test_copy_id_to_image(self):
        pass

    def test_revert_mapping(self):
        pass

    def test_apply_revert_mapping(self):
        pass

    def test_update_values_dict(self):
        pass
        
    '''

if __name__ == '__main__':
    unittest.main()
