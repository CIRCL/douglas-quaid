# -*- coding: utf-8 -*-

import logging
import pprint
import unittest

import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
import common.PerformanceDatastructs.stats_datastruct as stats_datastruct
from carlhauser_client.EvaluationTools.SimilarityGraphExtractor.similarity_graph_quality_evaluator import GraphQualityEvaluator
from common.ChartMaker.two_dimensions_plot import TwoDimensionsPlot
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.node import Node
from common.PerformanceDatastructs.thresholds_datastruct import Thresholds
from common.environment_variable import get_homedir


class TestPerformanceEvaluator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.output_folder = get_homedir() / "carlhauser_client_tests" / "graph_quality"
        self.quality_evaluator = GraphQualityEvaluator()
        self.quality_evaluator.TOLERANCE = 0.1  # We tolerate a 10% False Negative Rate / A 90% True positive rate "only"
        self.plotmaker = TwoDimensionsPlot()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def get_increasing_graph(self):
        perf_list = []

        MAX_VAL = 20
        for i in range(0, MAX_VAL):
            t = i / MAX_VAL
            tmp_score = stats_datastruct.Stats_datastruct()
            tmp_score.TPR = (i / MAX_VAL)
            perf_list.append(perf_datastruct.Perf(score=tmp_score, threshold=t))

        return perf_list

    def get_decreasing_graph(self):
        perf_list = []

        MAX_VAL = 20
        for i in range(0, MAX_VAL):
            t = i / MAX_VAL
            tmp_score = stats_datastruct.Stats_datastruct()
            tmp_score.TPR = 1 - (i / MAX_VAL)
            perf_list.append(perf_datastruct.Perf(score=tmp_score, threshold=t))

        return perf_list

    def get_real_graph(self):
        perf_list = []

        MAX_VAL = 20
        last_F1 = 0
        for i in range(0, MAX_VAL):
            t = i / MAX_VAL
            tmp_score = stats_datastruct.Stats_datastruct()

            delta = 0.05
            tmp_score.TPR = (i / MAX_VAL)  # Increasing
            tmp_score.FPR = (i / MAX_VAL) + delta  # Increasing
            tmp_score.TNR = 1 - (i / MAX_VAL)  # Decreasing
            tmp_score.FNR = 1 - (i / MAX_VAL) - delta  # Decreasing
            if i < MAX_VAL / 2:
                tmp_score.F1 = (i / MAX_VAL)  # Increasing until some point
                last_F1 = tmp_score.F1
            else:
                tmp_score.F1 = last_F1

            perf_list.append(perf_datastruct.Perf(score=tmp_score, threshold=t))

        return perf_list

    def test_get_max_max_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=True,
                                                                               maximize_threshold=True,
                                                                               is_increasing=True)
        self.logger.info(f"Found value {thre}")

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="max_max_inc.png")
        self.assertAlmostEqual(thre, 1.0, delta=0.1)

    def test_get_max_min_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=True,
                                                                               maximize_threshold=False,
                                                                               is_increasing=True)
        self.logger.info(f"Found value {thre}")

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="max_min_inc.png")
        self.assertAlmostEqual(thre, 0.8, delta=0.1)

    def test_get_min_max_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=False,
                                                                               maximize_threshold=True,
                                                                               is_increasing=True)
        self.logger.info(f"Found value {thre}")

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="min_max_inc.png")
        self.assertAlmostEqual(thre, 0.2, delta=0.1)

    def test_get_min_min_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=False,
                                                                               maximize_threshold=False,
                                                                               is_increasing=True)
        self.logger.info(f"Found value {thre}")

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="min_min_inc.png")
        self.assertAlmostEqual(thre, 0.0, delta=0.1)

    def test_get_max_max_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=False,
                                                                               maximize_threshold=False,
                                                                               is_increasing=False)
        self.logger.info(f"Found value {thre}")

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="max_max_dec.png")
        self.assertAlmostEqual(thre, 0.0, delta=0.1)

    def test_get_max_min_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=False,
                                                                               maximize_threshold=True,
                                                                               is_increasing=False)
        self.logger.info(f"Found value {thre}")

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="max_min_dex.png")
        self.assertAlmostEqual(thre, 0.2, delta=0.1)

    def test_get_min_max_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=True,
                                                                               maximize_threshold=False,
                                                                               is_increasing=False)
        self.logger.info(f"Found value {thre}")

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="min_max_dec.png")
        self.assertAlmostEqual(thre, 0.8, delta=0.1)

    def test_get_min_min_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               maximize_attribute=True,
                                                                               maximize_threshold=True,
                                                                               is_increasing=False)
        self.logger.info(f"Found value {thre}")
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=Thresholds(thre, 0, 0),
                                                   output_path=self.output_folder,
                                                   file_name="min_min_dec.png")
        self.assertAlmostEqual(thre, 1.0, delta=0.1)

    def test_real_graph(self):
        perf_list = self.get_real_graph()
        print([p.score.TPR for p in perf_list])
        print([p.score.TNR for p in perf_list])
        print([p.score.FPR for p in perf_list])
        print([p.score.FNR for p in perf_list])

        percent = 0.1

        thre_max_TPR, val_TPR = self.quality_evaluator.get_threshold_where_upper_are_more_than_xpercent_TP(perfs_list=perf_list, percent=percent)
        thre_max_FNR, val_FNR = self.quality_evaluator.get_threshold_where_upper_are_less_than_xpercent_FN(perfs_list=perf_list, percent=percent)
        thre_max_TNR, val_TNR = self.quality_evaluator.get_threshold_where_below_are_more_than_xpercent_TN(perfs_list=perf_list, percent=percent)
        thre_max_FPR, val_FPR = self.quality_evaluator.get_threshold_where_below_are_less_than_xpercent_FP(perfs_list=perf_list, percent=percent)
        thre_max_F1, val_F1 = self.quality_evaluator.get_max_threshold_for_max_F1(perfs_list=perf_list)

        self.logger.info(f"Found value TPR : {thre_max_TPR} for {val_TPR} / upper there is more than 90% true positive")
        self.logger.info(f"Found value TNR : {thre_max_TNR} for {val_TNR} / below there is more than 90% true negative")
        self.logger.info(f"Found value FNR : {thre_max_FNR} for {val_FNR} / upper there is less than 10% false negative")
        self.logger.info(f"Found value FPR : {thre_max_FPR} for {val_FPR} / below there is less than 10% false positive")
        self.logger.info(f"Found value F1 :  {thre_max_F1} for {val_F1}")

        thresholds = Thresholds(max_TPR=thre_max_TPR,
                                max_FNR=thre_max_FNR,
                                max_FPR=thre_max_FPR,
                                max_TNR=thre_max_TNR,
                                mean=thre_max_F1)
        thresholds.percent = percent
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=thresholds,
                                                   output_path=self.output_folder,
                                                   file_name="real_graph.png")

        self.assertAlmostEqual(thre_max_TPR, 0.8, delta=0.1)
        self.assertAlmostEqual(thre_max_TNR, 0.2, delta=0.1)
        self.assertAlmostEqual(thre_max_FNR, 0.8, delta=0.1)
        self.assertAlmostEqual(thre_max_FPR, 0.1, delta=0.1) # Would have been 0.2 without delta
        self.assertAlmostEqual(thre_max_F1, 0.5, delta=0.1)

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
        graph_data_struct.add_cluster(Cluster(label="A", id="A", image="A"))
        graph_data_struct.add_cluster(Cluster(label="B", id="B", image="B"))
        graph_data_struct.add_cluster(Cluster(label="C", id="C", image="C"))
        graph_data_struct.add_node(Node(label="1", id="1", image="1"))
        graph_data_struct.add_node(Node(label="2", id="2", image="2"))
        graph_data_struct.add_node(Node(label="3", id="3", image="3"))
        graph_data_struct.add_node(Node(label="4", id="4", image="4"))
        graph_data_struct.add_node(Node(label="5", id="5", image="5"))
        graph_data_struct.add_node(Node(label="6", id="6", image="6"))
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
        self.assertEqual(stats_datastruct.P, 3)
        self.assertEqual(stats_datastruct.N, 3)
        self.assertAlmostEqual(stats_datastruct.TPR, 0.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR, 1.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR, 0.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR, 1.0, delta=0.05)

        dist_threshold = 0.5
        stats_datastruct = quality_evaluator.compute_score_for_one_threshold(requests_results, graph_data_struct, dist_threshold)
        print(stats_datastruct)
        self.assertEqual(stats_datastruct.P, 3)
        self.assertEqual(stats_datastruct.N, 3)
        self.assertAlmostEqual(stats_datastruct.TPR, 0.66, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR, 0.33, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR, 0.66, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR, 0.33, delta=0.05)

        dist_threshold = 1
        stats_datastruct = quality_evaluator.compute_score_for_one_threshold(requests_results, graph_data_struct, dist_threshold)
        print(stats_datastruct)
        self.assertEqual(stats_datastruct.P, 3)
        self.assertEqual(stats_datastruct.N, 3)
        self.assertAlmostEqual(stats_datastruct.TPR, 1.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR, 0.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR, 1.0, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR, 0.0, delta=0.05)

        quality_evaluator.NB_TO_CHECK = 3

        dist_threshold = 0.5
        stats_datastruct = quality_evaluator.compute_score_for_one_threshold(requests_results, graph_data_struct, dist_threshold)
        print(stats_datastruct)
        self.assertEqual(stats_datastruct.P, 4)
        self.assertEqual(stats_datastruct.N, 3)
        self.assertAlmostEqual(stats_datastruct.TPR, 0.5, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.TNR, 0.33, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FPR, 0.66, delta=0.05)
        self.assertAlmostEqual(stats_datastruct.FNR, 0.5, delta=0.05)


if __name__ == '__main__':
    unittest.main()
