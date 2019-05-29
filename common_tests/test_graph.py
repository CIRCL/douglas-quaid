# -*- coding: utf-8 -*-

import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server_tests.context import *
import pathlib
import unittest
import pprint

from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
from common.Graph.metadata import Metadata, Source


class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        # self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")
        self.expected_json = {'clusters': [{'group': '',
                                            'id': 0,
                                            'image': '',
                                            'label': '',
                                            'members': ['0_0', '0_1', '0_2'],
                                            'shape': 'image'},
                                           {'group': '',
                                            'id': 1,
                                            'image': '',
                                            'label': '',
                                            'members': ['1_0', '1_1', '1_2'],
                                            'shape': 'image'}],
                              'edges': [{'color': 'gray', 'from': 0, 'to': '0_0'},
                                        {'color': 'gray', 'from': 0, 'to': '0_1'},
                                        {'color': 'gray', 'from': 0, 'to': '0_2'},
                                        {'color': 'gray', 'from': 1, 'to': '1_0'},
                                        {'color': 'gray', 'from': 1, 'to': '1_1'},
                                        {'color': 'gray', 'from': 1, 'to': '1_2'}],
                              'meta': {'source': 'DBDUMP'},
                              'nodes': [{'id': '0_0',
                                         'image': '',
                                         'label': 'picture name +0_0',
                                         'shape': 'image'},
                                        {'id': '0_1',
                                         'image': '',
                                         'label': 'picture name +0_1',
                                         'shape': 'image'},
                                        {'id': '0_2',
                                         'image': '',
                                         'label': 'picture name +0_2',
                                         'shape': 'image'},
                                        {'id': '1_0',
                                         'image': '',
                                         'label': 'picture name +1_0',
                                         'shape': 'image'},
                                        {'id': '1_1',
                                         'image': '',
                                         'label': 'picture name +1_1',
                                         'shape': 'image'},
                                        {'id': '1_2',
                                         'image': '',
                                         'label': 'picture name +1_2',
                                         'shape': 'image'}]}

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_graph(self):

        # Create a graphe structure
        tmp_meta = Metadata(Source.DBDUMP)
        tmp_graph = GraphDataStruct(tmp_meta)

        # For each cluster, fetch all pictures and store it
        for cluster_id in range(0, 2):
            tmp_graph.add_cluster(Cluster(label="", id=cluster_id, image=""))

            for id in range(0, 3):
                pic_id = str(cluster_id) + "_" + str(id)
                # Label = picture score, here
                tmp_graph.add_node(Node(label="picture name +" + pic_id, id=pic_id, image=""))
                tmp_graph.add_edge(Edge(_from=cluster_id, _to=pic_id))

        val = tmp_graph.export_as_json()
        pprint.pprint(val)

        self.assertDictEqual(val, self.expected_json)
