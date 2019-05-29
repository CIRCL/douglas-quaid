# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat

from carlhauser_server.Helpers.environment_variable import get_homedir

import carlhauser_client.Evaluator.cluster_matcher as cluster_matcher
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
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_client_tests/test_Helpers/id_generator")
        self.cluster_matcher = cluster_matcher.Cluster_matcher()

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_match_clusters_simple(self):
        setA = Cluster("big", 0, {'Python', 'R', 'SQL', 'Git', 'Tableau', 'SAS'})
        setB = Cluster("names", 1, {'toto', 'tata', 'ronron', 'gigi', 'lala', 'vava'})

        set1 = Cluster("similibig", 2, {'Python', 'R', 'Git', 'Tableau', 'SAS'})
        set2 = Cluster("similinames", 3, {'toto', 'tata', 'vava'})

        matching = self.cluster_matcher.match_clusters([setA, setB], [set1, set2])
        self.assertEqual(0, matching[0][0].id)
        self.assertEqual(2, matching[0][1].id)
        self.assertEqual(1, matching[1][0].id)
        self.assertEqual(3, matching[1][1].id)
        self.logger.info(pformat(matching))

    def test_match_clusters_median(self):
        setA = Cluster("big", 0, {'Python', 'R', 'SQL', 'Git', 'Tableau', 'SAS'})
        setB = Cluster("names", 1, {'toto', 'tata', 'ronron', 'gigi', 'lala', 'vava'})
        setC = Cluster("anim", 2, {'kalo', 'loka', 'lolo', 'kaka'})
        setD = Cluster("let", 3, {'bb', 'cc', 'aa'})

        set1 = Cluster("big", 4, {'Python', 'R', 'Git', 'Tableau', 'SAS'})
        set2 = Cluster("names", 5, {'toto', 'tata', 'vava'})
        set3 = Cluster("anim", 6, {'kalo', 'lolo'})
        set4 = Cluster("let", 7, {'bb'})

        matching = self.cluster_matcher.match_clusters([setA, setB, setC, setD], [set1, set2, set3, set4])
        self.assertEqual(0, matching[0][0].id)
        self.assertEqual(4, matching[0][1].id)
        self.assertEqual(1, matching[1][0].id)
        self.assertEqual(5, matching[1][1].id)
        self.assertEqual(2, matching[2][0].id)
        self.assertEqual(6, matching[2][1].id)
        self.assertEqual(3, matching[3][0].id)
        self.assertEqual(7, matching[3][1].id)

        self.logger.info(pformat(matching))

    def test_match_clusters_null(self):
        setA = Cluster("big", 0, {'Python', 'R'})
        setB = Cluster("null", 1, {""})

        set1 = Cluster("big", 2, {'Python'})
        set2 = Cluster("short", 3, {'R'})

        matching = self.cluster_matcher.match_clusters([setA, setB], [set1, set2])

        self.assertEqual(0, matching[0][0].id)
        self.assertEqual(2, matching[0][1].id)
        self.assertEqual(1, matching[1][0].id)
        self.assertEqual(3, matching[1][1].id)

        self.logger.info(pformat(matching))

    def test_set_storage(self):
        # Proof that sets are checked on their "content" and not their memory adress
        setA = {'Python', 'R'}
        setB = {""}

        set1 = {'Python', 'R'}
        set2 = {'R'}

        list_sets = [setA, setB, set1, set2]
        for i in list_sets:
            if i == setA:
                print("found ! ")


if __name__ == '__main__':
    unittest.main()
