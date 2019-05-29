# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat

from carlhauser_server.Helpers.environment_variable import get_homedir

import carlhauser_client.Evaluator.cluster_converter as cluster_converter
from carlhauser_client.Evaluator.cluster import Cluster, Node

class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_client_tests/test_Helpers/id_generator")
        self.cluster_converter = cluster_converter.Cluster_converter()

        self.db = {
            'clusters': [
                {
                    'id': 'cluster1',
                    'image': 'anchor.bmp',
                    'shape': 'image'
                },
                {
                    'id': 'cluster2',
                    'image': 'anchor.bmp',
                    'shape': 'image'
                },
                {
                    'id': 'cluster3',
                    'image': 'anchor.bmp',
                    'shape': 'image'
                }
            ],
            'edges': [
                {
                    'from': 'cluster1',
                    'title': '',
                    'to': '1',
                },
                {
                    'from': 'cluster1',
                    'title': '',
                    'to': '2',
                },
                {
                    'from': 'cluster1',
                    'title': '',
                    'to': '3',
                },
                {
                    'from': 'cluster3',
                    'title': '',
                    'to': '4',
                }
            ],
            'nodes': [
                {
                    'id': 'cluster1',
                    'image': 'anchor.bmp',
                    'shape': 'image'
                },
                {
                    'id': '1',
                    'image': '1.bmp',
                    'shape': 'image'
                },
                {
                    'id': '2',
                    'image': '2.bmp',
                    'shape': 'image'
                },
                {
                    'id': '3',
                    'image': '3.bmp',
                    'shape': 'image'
                },
                {
                    'id': '4',
                    'image': '4.bmp',
                    'shape': 'image'
                }
            ]
        }

        self.visjs = {
            "classes": [
                {
                    "label": "circl",
                    "members": [
                        6,
                        7
                    ],
                    "nb_item": 2
                },
                {
                    "label": "webmail",
                    "members": [
                        18,
                        19
                    ],
                    "nb_item": 2
                },
                {
                    "label": "wellsfargo",
                    "members": [
                        20
                    ],
                    "nb_item": 1
                }
            ],
            "nodes": [
                {
                    "id": 0,
                    "shape": "image",
                    "image": "404.png"
                },
                {
                    "id": 1,
                    "shape": "image",
                    "image": "advanzia1.png"
                },
                {
                    "id": 2,
                    "shape": "image",
                    "image": "advanzia2.png"
                },
                {
                    "id": 3,
                    "shape": "image",
                    "image": "advanzia3.png"
                },
                {
                    "id": 4,
                    "shape": "image",
                    "image": "advanzia4.png"
                },
                {
                    "id": 5,
                    "shape": "image",
                    "image": "alllogos.png"
                },
                {
                    "id": 6,
                    "shape": "image",
                    "image": "circl_secure.png"
                },
                {
                    "id": 7,
                    "shape": "image",
                    "image": "circl_webmail.png"
                },
                {
                    "id": "c13e9c15-d0ca-4240-9fc6-580bcd189177",
                    "shape": "image",
                    "image": "anchor.png",
                    "group": "anchor",
                    "label": "circl"
                },
                {
                    "id": "a490e50d-a014-454a-a0e6-216747eb8968",
                    "shape": "image",
                    "image": "anchor.png",
                    "group": "anchor",
                    "label": "webmail"
                },
                {
                    "id": "28459fb9-e754-4ee8-89d6-74165d15f4c9",
                    "shape": "image",
                    "image": "anchor.png",
                    "group": "anchor",
                    "label": "wellsfargo"
                }
            ]
        }

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_match_clusters_from_dump(self):
        matching = self.cluster_converter.convert_dump_to_clusters(self.db)

        self.logger.info(pformat(matching) + "\n")

        self.assertIn('1', matching[0].members)
        self.assertIn('2', matching[0].members)
        self.assertIn('3', matching[0].members)
        self.assertIn('4', matching[2].members)

    def test_match_clusters_from_visjs(self):
        matching = self.cluster_converter.convert_visjs_to_clusters(self.visjs)

        self.logger.info(pformat(matching) + "\n")

        self.assertIn(6, matching[0].members)
        self.assertIn(7, matching[0].members)
        self.assertIn(18, matching[1].members)
        self.assertIn(19, matching[1].members)
        self.assertIn(20, matching[2].members)


    def test_convert_mapping_to_visjs(self):

        '''
        cA = Cluster("A", "A", {Node(0, "O.jpg"), Node(1, "1.jpg"), Node(2, "2.jpg")})
        cB = Cluster("B", "B", {Node(7, "7.jpg"), Node(8, "8.jpg"), Node(9, "9.jpg")
                                ,Node(3, "3.jpg"), Node(4, "4.jpg"), Node(5, "5.jpg")
                                ,Node(6, "6.jpg")})

        c1 = Cluster("1", '1', {Node(0, "O.jpg"), Node(2, "2.jpg")})
        c2 = Cluster("2", "2", {Node(4, "4.jpg"), Node(5, "5.jpg"),Node(8, "8.jpg"), Node(9, "9.jpg")})

        '''

        cA = Cluster("A", "A", {0, 1, 2})
        cB = Cluster("B", "B", {4,5,6,7,8,9,10})

        c1 = Cluster("1", '1', {0, 2})
        c2 = Cluster("2", "2", {4,5,8,9,1})

        pair_list = [[cA, c1], [cB, c2]]

        visjs_graphe = self.cluster_converter.convert_mapping_to_visjs(pair_list)
        self.logger.info(pformat(visjs_graphe) + "\n")

        self.assertIn({'id': 0}, visjs_graphe["nodes"])
        self.assertIn({'id': 2}, visjs_graphe["nodes"])
        self.assertIn({'id': 7}, visjs_graphe["nodes"])
        self.assertIn({'id': 4}, visjs_graphe["nodes"])

        self.assertIn({'color': 'red', 'from': 'truth:B -> created:2', 'to': 1}, visjs_graphe["edges"])
        self.assertIn({'color': 'yellow', 'from': 'truth:B -> created:2', 'to': 7}, visjs_graphe["edges"])
        self.assertIn({'color': 'gray', 'from': 'truth:B -> created:2', 'to': 5}, visjs_graphe["edges"])

if __name__ == '__main__':
    unittest.main()
