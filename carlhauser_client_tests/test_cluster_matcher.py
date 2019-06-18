# -*- coding: utf-8 -*-

import unittest
import logging
import pathlib
from pprint import pformat

from carlhauser_server.Helpers.environment_variable import get_homedir

import carlhauser_client.EvaluationTools.ClassificationQuality.cluster_matcher as cluster_matcher
from common.Graph.cluster import Cluster


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
        setA = Cluster("big", 0, "")
        setA.add_member_id('Python')
        setA.add_member_id('R')
        setA.add_member_id('SQL')
        setA.add_member_id('Git')
        setA.add_member_id('Tableau')
        setA.add_member_id('SAS')
        setB = Cluster("names", 1, "")
        setB.add_member_id('toto')
        setB.add_member_id('tata')
        setB.add_member_id('ronron')
        setB.add_member_id('gigi')
        setB.add_member_id('lala')
        setB.add_member_id('vava')

        set1 = Cluster("similibig", 2, "")
        set1.add_member_id('Python')
        set1.add_member_id('R')
        set1.add_member_id('Git')
        set1.add_member_id('Tableau')
        set1.add_member_id('SAS')
        set2 = Cluster("similinames", 3, "")
        set2.add_member_id('toto')
        set2.add_member_id('tata')
        set2.add_member_id('vava')

        matching = self.cluster_matcher.match_clusters([setA, setB], [set1, set2])
        self.assertEqual(0, matching[0][0].id)
        self.assertEqual(2, matching[0][1].id)
        self.assertEqual(1, matching[1][0].id)
        self.assertEqual(3, matching[1][1].id)
        self.logger.info(pformat(matching))

    def test_match_clusters_median(self):
        setA = Cluster("big", 0, "")
        setA.add_member_id('Python')
        setA.add_member_id('R')
        setA.add_member_id('SQL')
        setA.add_member_id('Git')
        setA.add_member_id('Tableau')
        setA.add_member_id('SAS')
        setB = Cluster("names", 1, "")
        setB.add_member_id('toto')
        setB.add_member_id('tata')
        setB.add_member_id('ronron')
        setB.add_member_id('gigi')
        setB.add_member_id('lala')
        setB.add_member_id('vava')
        setC = Cluster("anim", 2, "")
        setC.add_member_id('kalo')
        setC.add_member_id('loka')
        setC.add_member_id('lolo')
        setC.add_member_id('kaka')
        setD = Cluster("let", 3, "")
        setD.add_member_id('bb')
        setD.add_member_id('cc')
        setD.add_member_id('aa')


        set1 = Cluster("big", 4, "")
        set1.add_member_id('Python')
        set1.add_member_id('R')
        set1.add_member_id('Git')
        set1.add_member_id('Tableau')
        set1.add_member_id('SAS')
        set2 = Cluster("names", 5, "")
        set2.add_member_id('toto')
        set2.add_member_id('tata')
        set2.add_member_id('vava')
        set3 = Cluster("anim", 6, "")
        set3.add_member_id('kalo')
        set3.add_member_id('lolo')
        set4 = Cluster("let", 7, "")
        set4.add_member_id('bb')


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
        setA = Cluster("big", 0, "")
        setA.add_member_id('Python')
        setA.add_member_id('R')
        setB = Cluster("null", 1, "")
        setB.add_member_id('')

        set1 = Cluster("big", 2, "")
        set1.add_member_id('Python')
        set2 = Cluster("short", 3, "")
        set2.add_member_id('R')

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
