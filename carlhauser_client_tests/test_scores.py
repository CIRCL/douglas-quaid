# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
import pprint

from carlhauser_server.Helpers.environment_variable import get_homedir

import carlhauser_client.Evaluator.scores as scores
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
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_client_tests/evaluator/confusion_matrix")

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_merge_scores(self):
        s1 = scores.Scoring()
        s2 = scores.Scoring()

        truth_set = set({2,3,4})
        candidate_set_1 = set({1,2,3})
        candidate_set_2 = set({2,3,4,5,6})
        s1.compute_all(truth_set, candidate_set_1, 6)
        s2.compute_all(truth_set, candidate_set_2, 6)

        total = scores.merge_scores([s1,s2])
        pprint.pprint(total)

        self.assertEqual(total.ACC,(s1.ACC+s2.ACC)/2)
        self.assertEqual(total.F1,(s1.F1+s2.F1)/2)
        self.assertEqual(total.TPR,(s1.TPR+s2.TPR)/2)



if __name__ == '__main__':
    unittest.main()
