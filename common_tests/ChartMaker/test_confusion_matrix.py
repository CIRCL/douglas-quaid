# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib

from common.environment_variable import get_homedir

import common.ChartMaker.confusion_matrix_generator as confusion_matrix_generator
from common.Graph.cluster import Cluster


class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / "datasets" / "TEST_DATASETS" / "confusion_matrix"
        self.matrix_gen = confusion_matrix_generator.ConfusionMatrixGenerator()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_match_clusters_from_dump(self):
        cA = Cluster("A", "A", {0, 1, 2})
        cB = Cluster("B", "B", {4, 5, 6, 7, 8, 9, 10})

        c1 = Cluster("1", '1', {0, 2})
        c2 = Cluster("2", "2", {4, 5, 8, 9})

        self.matrix_gen.create_and_export_confusion_matrix([cA, cB], [c1, c2], self.test_file_path / "matrix.pdf")


if __name__ == '__main__':
    unittest.main()
