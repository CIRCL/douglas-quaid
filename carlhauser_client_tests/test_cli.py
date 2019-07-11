# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat

from common.environment_variable import get_homedir

import carlhauser_client.EvaluationTools.Internal_clustering_Quality_Evaluator.cluster_matcher as cluster_matcher
from common.Graph.cluster import Cluster


class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    ''' 
    # TODO !
    def test_ping(self):
        pass

    def test_upload(self):
        pass

    def test_request(self):
        pass

    def test_dump(self):
        pass
    '''

if __name__ == '__main__':
    unittest.main()
