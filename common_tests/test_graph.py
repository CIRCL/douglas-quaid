# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.pardir))
import unittest
import pprint

from common.Graph.graph_datastructure import GraphDataStruct
import common.Graph.graph_datastructure as graph_datastructure
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
from common.Graph.metadata import Metadata, Source


class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.maxDiff = None
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

        self.mappedexpected = {'clusters': [{'group': '',
                                             'id': 0,
                                             'image': '',
                                             'label': '',
                                             'members': ['0_0NEW', '0_1NEW', '0_2NEW'],
                                             'shape': 'image'},
                                            {'group': '',
                                             'id': 1,
                                             'image': '',
                                             'label': '',
                                             'members': ['1_0NEW', '1_1NEW', '1_2NEW'],
                                             'shape': 'image'}],
                               'edges': [{'color': 'gray', 'from': 0, 'to': '0_0NEW'},
                                         {'color': 'gray', 'from': 0, 'to': '0_1NEW'},
                                         {'color': 'gray', 'from': 0, 'to': '0_2NEW'},
                                         {'color': 'gray', 'from': 1, 'to': '1_0NEW'},
                                         {'color': 'gray', 'from': 1, 'to': '1_1NEW'},
                                         {'color': 'gray', 'from': 1, 'to': '1_2NEW'}],
                               'meta': {'source': 'DBDUMP'},
                               'nodes': [{'id': '0_0NEW',
                                          'image': '0_0IMAGE',
                                          'label': 'picture name +0_0OLD',
                                          'shape': 'image'},
                                         {'id': '0_1NEW',
                                          'image': '0_1IMAGE',
                                          'label': 'picture name +0_1OLD',
                                          'shape': 'image'},
                                         {'id': '0_2NEW',
                                          'image': '0_2IMAGE',
                                          'label': 'picture name +0_2OLD',
                                          'shape': 'image'},
                                         {'id': '1_0NEW',
                                          'image': '1_0IMAGE',
                                          'label': 'picture name +1_0OLD',
                                          'shape': 'image'},
                                         {'id': '1_1NEW',
                                          'image': '1_1IMAGE',
                                          'label': 'picture name +1_1OLD',
                                          'shape': 'image'},
                                         {'id': '1_2NEW',
                                          'image': '1_2IMAGE',
                                          'label': 'picture name +1_2OLD',
                                          'shape': 'image'}]}

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_graph_export(self):

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

        print("Exported dict : ")
        val = tmp_graph.export_as_dict()
        pprint.pprint(val)

        self.assertDictEqual(val, self.expected_json)

    def test_graph_import_export_consistency(self):

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

        print("Exported dict : ")
        val = tmp_graph.export_as_dict()
        pprint.pprint(val)
        print("Import graphe : ")
        new_graph = GraphDataStruct.load_from_dict(val)
        pprint.pprint(new_graph)
        print("Exported dict (after import): ")
        new_val = new_graph.export_as_dict()
        pprint.pprint(new_val)

        self.assertDictEqual(val, self.expected_json)
        self.assertDictEqual(val, new_val)

    def test_graph_image_to_id_mapping_conversion(self):

        mapping = {}

        # Create a graphe structure
        tmp_meta = Metadata(Source.DBDUMP)
        tmp_graph = GraphDataStruct(tmp_meta)

        # For each cluster, fetch all pictures and store it
        for cluster_id in range(0, 2):
            tmp_graph.add_cluster(Cluster(label="", id=cluster_id, image=""))

            for id in range(0, 3):
                pic_id = str(cluster_id) + "_" + str(id) + "OLD"
                pic_image = str(cluster_id) + "_" + str(id) + "IMAGE"

                # Prepare mapping
                mapping[pic_image] = str(cluster_id) + "_" + str(id) + "NEW"

                # Label = picture score, here
                tmp_graph.add_node(Node(label="picture name +" + pic_id, id=pic_id, image=pic_image))
                tmp_graph.add_edge(Edge(_from=cluster_id, _to=pic_id))

        print("Exported dict : ")
        val = tmp_graph.export_as_dict()
        pprint.pprint(val)

        print("Mapping: ")
        pprint.pprint(mapping)

        tmp_graph.replace_id_from_mapping(mapping)

        print("Mapped: ")
        val = tmp_graph.export_as_dict()
        pprint.pprint(val)

        self.assertDictEqual(val, self.mappedexpected)

    def test_get_clusters_list(self):

        # Create a graphe structure
        tmp_meta = Metadata(Source.DBDUMP)
        tmp_graph = GraphDataStruct(tmp_meta)

        # For each cluster, fetch all pictures and store it
        for cluster_id in range(0, 2):
            tmp_graph.add_cluster(Cluster(label="", id=cluster_id, image=""))

            for id in range(0, 3):
                pic_id = str(cluster_id) + "_" + str(id) + "OLD"
                pic_image = str(cluster_id) + "_" + str(id) + "IMAGE"

                # Label = picture score, here
                tmp_graph.add_node(Node(label="picture name +" + pic_id, id=pic_id, image=pic_image))
                tmp_graph.add_edge(Edge(_from=cluster_id, _to=pic_id))

        print("Exported dict : ")
        val = tmp_graph.export_as_dict()
        pprint.pprint(val)

        cluster_list = [c.export_as_dict() for c in tmp_graph.get_clusters()]
        print("Cluster list : ")
        pprint.pprint(cluster_list)

        self.assertListEqual(cluster_list, [{'group': '',
                                             'id': 0,
                                             'image': '',
                                             'label': '',
                                             'members': ['0_0OLD', '0_1OLD', '0_2OLD'],
                                             'shape': 'image'
                                             },
                                            {'group': '',
                                             'id': 1,
                                             'image': '',
                                             'label': '',
                                             'members': ['1_0OLD', '1_1OLD', '1_2OLD'],
                                             'shape': 'image'}
                                            ]
                             )

    def test_merge_graphs(self):

        # Create a graphe structure
        tmp_meta = Metadata(Source.DBDUMP)
        tmp_graph = GraphDataStruct(tmp_meta)

        # For each cluster, fetch all pictures and store it
        for cluster_id in range(0, 2):
            tmp_graph.add_cluster(Cluster(label="", id=cluster_id, image=""))

            for id in range(0, 3):
                pic_id = str(cluster_id) + "_" + str(id) + "OLD"
                pic_image = str(cluster_id) + "_" + str(id) + "IMAGE"

                # Label = picture score, here
                tmp_graph.add_node(Node(label="picture name +" + pic_id, id=pic_id, image=pic_image))
                tmp_graph.add_edge(Edge(_from=cluster_id, _to=pic_id))

        # Create a graphe structure
        tmp_meta = Metadata(Source.VISJS)
        tmp_graph_vis = GraphDataStruct(tmp_meta)

        # For each cluster, fetch all pictures and store it
        for cluster_id in range(0, 2):
            tmp_graph_vis.add_cluster(Cluster(label="", id=cluster_id, image=""))

            for id in range(0, 3):
                pic_id = str(cluster_id) + "_" + str(id) + "OLD"
                pic_image = str(cluster_id) + "_" + str(id) + "IMAGE"

                # Label = picture score, here
                tmp_graph_vis.add_node(Node(label="picture name +" + pic_id, id=pic_id, image=pic_image))
                tmp_graph_vis.add_edge(Edge(_from=cluster_id, _to=pic_id))

        cluster_mapping = [[Cluster("", 0, ""), Cluster("", 0, "")],
                           [Cluster("", 1, ""), Cluster("", 2, "")],
                           [Cluster("", 2, ""), Cluster("", 1, "")]]

        print("Exported db dict : ")
        val = tmp_graph.export_as_dict()
        pprint.pprint(val)

        print("Exported tmp_graph_vis : ")
        val = tmp_graph_vis.export_as_dict()
        pprint.pprint(val)

        print("New graph : ")
        new_graph = graph_datastructure.merge_graphs(tmp_graph_vis, tmp_graph, cluster_mapping)
        pprint.pprint(new_graph)

        self.assertDictEqual(new_graph, {'clusters': [{'group': '',
                                                       'id': 0,
                                                       'image': '',
                                                       'label': '',
                                                       'members': ['0_0OLD', '0_1OLD', '0_2OLD'],
                                                       'shape': 'image'},
                                                      {'group': '',
                                                       'id': 1,
                                                       'image': '',
                                                       'label': '',
                                                       'members': ['1_0OLD', '1_1OLD', '1_2OLD'],
                                                       'shape': 'image'}],
                                         'edges': [{'color': {'color': 'green'}, 'from': '0_0OLD', 'to': 0},
                                                   {'color': {'color': 'green'}, 'from': '0_1OLD', 'to': 0},
                                                   {'color': {'color': 'green'}, 'from': '0_2OLD', 'to': 0},
                                                   {'color': {'color': 'orange'}, 'from': '1_0OLD', 'to': 1},
                                                   {'color': {'color': 'red'}, 'from': '1_0OLD', 'to': 2},
                                                   {'color': {'color': 'orange'}, 'from': '1_1OLD', 'to': 1},
                                                   {'color': {'color': 'red'}, 'from': '1_1OLD', 'to': 2},
                                                   {'color': {'color': 'orange'}, 'from': '1_2OLD', 'to': 1},
                                                   {'color': {'color': 'red'}, 'from': '1_2OLD', 'to': 2}],
                                         'meta_1': {'source': 'VISJS'},
                                         'meta_2': {'source': 'DBDUMP'},
                                         'nodes': [{'id': '0_0OLD',
                                                    'image': '0_0IMAGE',
                                                    'label': 'picture name +0_0OLD',
                                                    'shape': 'image'},
                                                   {'id': '0_1OLD',
                                                    'image': '0_1IMAGE',
                                                    'label': 'picture name +0_1OLD',
                                                    'shape': 'image'},
                                                   {'id': '0_2OLD',
                                                    'image': '0_2IMAGE',
                                                    'label': 'picture name +0_2OLD',
                                                    'shape': 'image'},
                                                   {'id': '1_0OLD',
                                                    'image': '1_0IMAGE',
                                                    'label': 'picture name +1_0OLD',
                                                    'shape': 'image'},
                                                   {'id': '1_1OLD',
                                                    'image': '1_1IMAGE',
                                                    'label': 'picture name +1_1OLD',
                                                    'shape': 'image'},
                                                   {'id': '1_2OLD',
                                                    'image': '1_2IMAGE',
                                                    'label': 'picture name +1_2OLD',
                                                    'shape': 'image'}]})

    def test_edges_with_colors(self):

        vis_js_edges = {"1": "cluster1",
                        "2": "cluster2",
                        "3": "cluster3"}

        db_edges = {"1": "cluster1",
                    "2": "cluster3"}

        edge_list = graph_datastructure.merge_edges_with_colors(vis_js_edges, db_edges)

        print("Exported edge_list : ")
        pprint.pprint(edge_list)

        self.assertTrue(edge_list[0].color, "green")
        self.assertTrue(edge_list[1].color, "red")
        self.assertTrue(edge_list[2].color, "orange")
        self.assertTrue(edge_list[3].color, "black")
