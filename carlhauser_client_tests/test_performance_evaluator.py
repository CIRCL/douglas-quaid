# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat

from carlhauser_server.Helpers.environment_variable import get_homedir

import carlhauser_client.Evaluator.performance_evaluation as performance_evaluation
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
from common.Graph.metadata import Metadata, Source

class TestPerformanceEvaluator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_client_tests/test_Helpers/id_generator")
        self.perf = performance_evaluation.Performance_Evaluator()

    def test_absolute_truth_and_meaning(self):
        assert True

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
        for i in {0, 2} :
            c1.add_member_id(i)

        c2 = Cluster("2", "2", "")
        for i in {4,5,8,9} :
            c2.add_member_id(i)

        pair_list = [[cA, c1], [cB, c2]]

        self.logger.info(pformat(pair_list) + "\n")

        pair_list = self.perf.evaluate_performance(pair_list, 11)

        self.logger.info(pformat(pair_list) + "\n")


if __name__ == '__main__':
    unittest.main()
