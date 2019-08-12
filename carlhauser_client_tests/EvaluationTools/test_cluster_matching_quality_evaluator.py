# -*- coding: utf-8 -*-

import logging
import unittest
from pprint import pformat

import carlhauser_client.EvaluationTools.StorageGraphExtractor.cluster_matching_quality_evaluator as performance_evaluation
from common.Graph.cluster import Cluster
from common.PerformanceDatastructs.clustermatch_datastruct import ClusterMatch
from common.environment_variable import get_homedir


class TestClusterMatchingQualityEvaluator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / "datasets" / "douglas-quaid-tests" / "id_generator"
        self.perf = performance_evaluation.ClusterMatchingQualityEvaluator()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_evaluate_performance(self):

        cA = Cluster("A", "A", "")
        cA.add_member_id(0)
        cA.add_member_id(1)
        cA.add_member_id(2)

        cB = Cluster("B", "B", "")
        cB.add_member_id(4)
        cB.add_member_id(5)
        cB.add_member_id(6)
        cB.add_member_id(7)
        cB.add_member_id(8)
        cB.add_member_id(9)
        cB.add_member_id(10)

        c1 = Cluster("1", '1', "")
        for i in {0, 2}:
            c1.add_member_id(i)

        c2 = Cluster("2", "2", "")
        for i in {4, 5, 8, 9}:
            c2.add_member_id(i)

        pair_list = [ClusterMatch(cA, c1), ClusterMatch(cB, c2)]

        self.logger.info(pformat(pair_list) + "\n")

        pair_list = self.perf.evaluate_performance(pair_list, 11)

        self.logger.info(pformat(pair_list) + "\n")


if __name__ == '__main__':
    unittest.main()
