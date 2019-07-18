# -*- coding: utf-8 -*-

import logging
import unittest

import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
from carlhauser_server.Configuration.algo_conf import Algo_conf


class TestInMemoryOperations(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/Configuration")

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_calibrated_algos_to_conf_file(self):
        list_algo_conf = []

        # Create list of algo conf
        list_algo_conf.append(Algo_conf("A_HASH", False, 0.0, 0.3, distance_weight=1))
        list_algo_conf.append(Algo_conf("P_HASH", True, 0.1, 0.4, distance_weight=2))
        list_algo_conf.append(Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.5, distance_weight=3))
        list_algo_conf.append(Algo_conf("D_HASH", True, 0.3, 0.6, distance_weight=4))
        list_algo_conf.append(Algo_conf("D_HASH_VERTICAL", False, 0.4, 0.7, distance_weight=5))
        list_algo_conf.append(Algo_conf("W_HASH", False, 0.5, 0.8, distance_weight=6))
        list_algo_conf.append(Algo_conf("TLSH", True, 0.6, 0.9, distance_weight=7))
        list_algo_conf.append(Algo_conf("ORB", True, 0.7, 1.0, distance_weight=8))

        # Generate conf file from algo_conf list
        fe_conf = feature_extractor_conf.calibrated_algos_to_conf_file(list_algo_conf)

        # Verify if correct
        self.assertEqual(fe_conf.A_HASH.is_enabled, False)
        self.assertEqual(fe_conf.D_HASH.is_enabled, True)
        self.assertEqual(fe_conf.TLSH.is_enabled, True)
        self.assertEqual(fe_conf.ORB.is_enabled, True)

        self.assertAlmostEqual(fe_conf.A_HASH.threshold_yes_to_maybe, 0.0, delta=0.05)
        self.assertAlmostEqual(fe_conf.P_HASH.threshold_yes_to_maybe, 0.1, delta=0.05)
        self.assertAlmostEqual(fe_conf.D_HASH.threshold_yes_to_maybe, 0.3, delta=0.05)
        self.assertAlmostEqual(fe_conf.TLSH.threshold_yes_to_maybe, 0.6, delta=0.05)
        self.assertAlmostEqual(fe_conf.ORB.threshold_yes_to_maybe, 0.7, delta=0.05)

        self.assertAlmostEqual(fe_conf.A_HASH.threshold_maybe_to_no, 0.3, delta=0.05)
        self.assertAlmostEqual(fe_conf.P_HASH.threshold_maybe_to_no, 0.4, delta=0.05)
        self.assertAlmostEqual(fe_conf.D_HASH.threshold_maybe_to_no, 0.6, delta=0.05)
        self.assertAlmostEqual(fe_conf.TLSH.threshold_maybe_to_no, 0.9, delta=0.05)
        self.assertAlmostEqual(fe_conf.ORB.threshold_maybe_to_no, 1.0, delta=0.05)

    def test_calibrated_algos_to_conf_file_partial(self):
        list_algo_conf = []

        # Create list of algo conf
        list_algo_conf.append(Algo_conf("A_HASH", False, 0.0, 0.3, distance_weight=1))
        # self.P_HASH: Algo_conf = Algo_conf("P_HASH", True, 0.2, 0.6, distance_weight=1)
        list_algo_conf.append(Algo_conf("P_HASH_SIMPLE", False, 0.2, 0.5, distance_weight=3))
        # self.D_HASH: Algo_conf = Algo_conf("D_HASH", True, 0.2, 0.6, distance_weight=1)
        list_algo_conf.append(Algo_conf("D_HASH_VERTICAL", False, 0.4, 0.7, distance_weight=5))
        # self.W_HASH: Algo_conf = Algo_conf("W_HASH", False, 0.2, 0.6, distance_weight=1)
        list_algo_conf.append(Algo_conf("TLSH", True, 0.6, 0.9, distance_weight=7))
        list_algo_conf.append(Algo_conf("ORB", True, 0.7, 1.0, distance_weight=8))

        # Generate conf file from algo_conf list
        fe_conf = feature_extractor_conf.calibrated_algos_to_conf_file(list_algo_conf)

        # Verify if correct
        self.assertEqual(fe_conf.A_HASH.is_enabled, False)
        self.assertEqual(fe_conf.D_HASH.is_enabled, True)
        self.assertEqual(fe_conf.TLSH.is_enabled, True)
        self.assertEqual(fe_conf.ORB.is_enabled, True)

        self.assertAlmostEqual(fe_conf.A_HASH.threshold_yes_to_maybe, 0.0, delta=0.05)
        self.assertAlmostEqual(fe_conf.P_HASH.threshold_yes_to_maybe, 0.2, delta=0.05)
        self.assertAlmostEqual(fe_conf.D_HASH.threshold_yes_to_maybe, 0.2, delta=0.05)
        self.assertAlmostEqual(fe_conf.TLSH.threshold_yes_to_maybe, 0.6, delta=0.05)
        self.assertAlmostEqual(fe_conf.ORB.threshold_yes_to_maybe, 0.7, delta=0.05)

        self.assertAlmostEqual(fe_conf.A_HASH.threshold_maybe_to_no, 0.3, delta=0.05)
        self.assertAlmostEqual(fe_conf.P_HASH.threshold_maybe_to_no, 0.6, delta=0.05)
        self.assertAlmostEqual(fe_conf.D_HASH.threshold_maybe_to_no, 0.6, delta=0.05)
        self.assertAlmostEqual(fe_conf.TLSH.threshold_maybe_to_no, 0.9, delta=0.05)
        self.assertAlmostEqual(fe_conf.ORB.threshold_maybe_to_no, 1.0, delta=0.05)


if __name__ == '__main__':
    unittest.main()
