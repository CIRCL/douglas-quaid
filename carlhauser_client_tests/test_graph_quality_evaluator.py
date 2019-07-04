# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat
import pprint

from common.environment_variable import get_homedir

import carlhauser_client.EvaluationTools.Internal_clustering_Quality_Evaluator.cluster_matching_quality_evaluator as performance_evaluation
from common.Graph.cluster import Cluster
from common.Graph.node import Node
from common.Graph.edge import Edge
from common.Graph.metadata import Metadata, Source
from common.Graph.graph_datastructure import GraphDataStruct
from carlhauser_client.EvaluationTools.GraphExtraction.graph_quality_evaluator import GraphQualityEvaluator


class TestPerformanceEvaluator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_compute_score_for_one_threshold(self):
        # Graph example. Please check documentation for more information
        quality_evaluator = GraphQualityEvaluator()

        requests_results = [
            # 1 to 2 and 3
            {
                "list_pictures": [
                    {
                        "cluster_id": "XXX",
                        "decision": "YES",
                        "distance": 0.1,
                        "image_id": "2"
                    },
                    {
                        "cluster_id": "XXX",
                        "decision": "YES",
                        "distance": 0.6,
                        "image_id": "3"
                    }
                ],
                "request_id": "1",
                "status": "matches_found",
                "request_time": 0
            },
            {
                "list_pictures": [
                    {
                        "cluster_id": "XXX",
                        "decision": "YES",
                        "distance": 0.3,
                        "image_id": "6"
                    }
                ],
                "request_id": "2",
                "status": "matches_found",
                "request_time": 0
            },
            {
                "list_pictures": [
                    {
                        "cluster_id": "XXX",
                        "decision": "YES",
                        "distance": 0.2,
                        "image_id": "1"
                    }
                ],
                "request_id": "3",
                "status": "matches_found",
                "request_time": 0
            },
            {
                "list_pictures": [
                    {
                        "cluster_id": "XXX",
                        "decision": "YES",
                        "distance": 0.4,
                        "image_id": "2"
                    }
                ],
                "request_id": "4",
                "status": "matches_found",
                "request_time": 0
            },
            {
                "list_pictures": [
                    {
                        "cluster_id": "XXX",
                        "decision": "YES",
                        "distance": 0.6,
                        "image_id": "4"
                    }
                ],
                "request_id": "5",
                "status": "matches_found",
                "request_time": 0
            },
            {
                "list_pictures": [
                    {
                        "cluster_id": "XXX",
                        "decision": "YES",
                        "distance": 0.7,
                        "image_id": "2"
                    }
                ],
                "request_id": "6",
                "status": "matches_found",
                "request_time": 0
            }
        ]

        # Create the reference graph
        graph_data_struct = GraphDataStruct(Metadata(Source.DBDUMP))
        graph_data_struct.add_cluster(Cluster(label= "A", id="A", image="A"))
        graph_data_struct.add_cluster(Cluster(label= "B", id="B", image="B"))
        graph_data_struct.add_cluster(Cluster(label= "C", id="C", image="C"))
        graph_data_struct.add_node(Node(label= "1", id= "1", image="1"))
        graph_data_struct.add_node(Node(label= "2", id= "2", image="2"))
        graph_data_struct.add_node(Node(label= "3", id= "3", image="3"))
        graph_data_struct.add_node(Node(label= "4", id= "4", image="4"))
        graph_data_struct.add_node(Node(label= "5", id= "5", image="5"))
        graph_data_struct.add_node(Node(label= "6", id= "6", image="6"))
        graph_data_struct.add_edge(Edge(_from="1", _to="A"))
        graph_data_struct.add_edge(Edge(_from="2", _to="A"))
        graph_data_struct.add_edge(Edge(_from="3", _to="A"))
        graph_data_struct.add_edge(Edge(_from="4", _to="B"))
        graph_data_struct.add_edge(Edge(_from="5", _to="B"))
        graph_data_struct.add_edge(Edge(_from="6", _to="C"))

        pprint.pprint(requests_results)
        pprint.pprint(graph_data_struct.export_as_dict())

        quality_evaluator.NB_TO_CHECK = 1

        dist_threshold = 0
        stats_datastruct = quality_evaluator.compute_score_for_one_threshold(requests_results, graph_data_struct, dist_threshold)
        print(stats_datastruct)
        self.assertEqual(stats_datastruct.P , 3)
        self.assertEqual(stats_datastruct.N , 3)
        self.assertAlmostEqual(stats_datastruct.TPR , 0.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR , 1.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR , 0.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR , 1.0, delta=0.05)


        dist_threshold = 0.5
        stats_datastruct = quality_evaluator.compute_score_for_one_threshold(requests_results, graph_data_struct, dist_threshold)
        print(stats_datastruct)
        self.assertEqual(stats_datastruct.P , 3)
        self.assertEqual(stats_datastruct.N , 3)
        self.assertAlmostEqual(stats_datastruct.TPR , 0.66, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR , 0.33, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR , 0.66, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR , 0.33, delta=0.05)

        dist_threshold = 1
        stats_datastruct = quality_evaluator.compute_score_for_one_threshold(requests_results, graph_data_struct, dist_threshold)
        print(stats_datastruct)
        self.assertEqual(stats_datastruct.P , 3)
        self.assertEqual(stats_datastruct.N , 3)
        self.assertAlmostEqual(stats_datastruct.TPR , 1.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR , 0.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR , 1.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR , 0.0, delta=0.05)

        quality_evaluator.NB_TO_CHECK = 3

        dist_threshold = 0.5
        stats_datastruct = quality_evaluator.compute_score_for_one_threshold(requests_results, graph_data_struct, dist_threshold)
        print(stats_datastruct)
        self.assertEqual(stats_datastruct.P , 4)
        self.assertEqual(stats_datastruct.N , 3)
        self.assertAlmostEqual(stats_datastruct.TPR , 0.5, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR , 0.33, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR , 0.66, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR , 0.5, delta=0.05)

if __name__ == '__main__':
    unittest.main()
