# -*- coding: utf-8 -*-

import logging
import os
import sys
import pprint

sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
from common.Calibrator.calibrator_conf import Default_calibrator_conf
from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.ImportExport.json_import_export import Custom_JSON_Encoder

import unittest


class test_calibrator_conf(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        # self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")
        self.calibrator_conf = Default_calibrator_conf()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_validate_0(self):
        # Verify if FPR + TNR is bad

        self.calibrator_conf.Acceptable_false_positive_rate = 0.5
        self.calibrator_conf.Minimum_true_negative_rate = 0.5
        try:
            self.calibrator_conf.validate()
            self.assertTrue(False)
        except Exception as e:
            self.assertTrue(True)

    def test_validate_1(self):
        # Verify if FPR + FNR is good
        self.calibrator_conf.Acceptable_false_positive_rate = 0.5
        self.calibrator_conf.Acceptable_false_negative_rate = 0.5
        try:
            self.calibrator_conf.validate()
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

    def test_validate_2(self):
        # Verify if TPR + TNR is good

        self.calibrator_conf.Minimum_true_positive_rate = 0.5
        self.calibrator_conf.Minimum_true_negative_rate = 0.5
        try:
            self.calibrator_conf.validate()
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

    def test_validate_3(self):
        # Verify if FNR + TPR is bad

        self.calibrator_conf.Acceptable_false_negative_rate = 0.5
        self.calibrator_conf.Minimum_true_positive_rate = 0.5
        try:
            self.calibrator_conf.validate()
            self.assertTrue(False)
        except Exception as e:
            self.assertTrue(True)

    def test_good_pair_0(self):
        # Verify if FPR + TNR is bad

        self.calibrator_conf.Acceptable_false_positive_rate = 0.1
        self.calibrator_conf.Minimum_true_negative_rate = 0.9
        try:
            pair0, pair1 = self.calibrator_conf.return_good_pair()
            self.assertEqual(pair0.rate, 0.1)
            self.assertEqual(pair1.rate, 0.9)
        except Exception as e:
            self.assertTrue(True)

    def test_good_pair_1(self):
        # Verify if FPR + FNR is good
        self.calibrator_conf.Acceptable_false_positive_rate = 0.1
        self.calibrator_conf.Acceptable_false_negative_rate = 0.9
        try:
            pair0, pair1 = self.calibrator_conf.return_good_pair()
            self.assertEqual(pair0.rate, 0.1)
            self.assertEqual(pair1.rate, 0.9)
        except Exception as e:
            self.assertTrue(False)

    def test_good_pair_2(self):
        # Verify if TPR + TNR is good

        self.calibrator_conf.Minimum_true_positive_rate = 0.1
        self.calibrator_conf.Minimum_true_negative_rate = 0.9
        try:
            pair0, pair1 = self.calibrator_conf.return_good_pair()
            self.assertEqual(pair0.rate, 0.9)
            self.assertEqual(pair1.rate, 0.1)
        except Exception as e:
            self.assertTrue(False)

    def test_good_pair_3(self):
        # Verify if FNR + TPR is bad

        self.calibrator_conf.Acceptable_false_negative_rate = 0.1
        self.calibrator_conf.Minimum_true_negative_rate = 0.9
        try:
            pair0, pair1 = self.calibrator_conf.return_good_pair()
            self.assertEqual(pair0.rate, 0.9)
            self.assertEqual(pair1.rate, 0.1)
        except Exception as e:
            self.assertTrue(False)

    def test_export_to_algo(self):
        tmp_conf = Algo_conf(algo_name="ORB",
                             is_enabled=False,
                             threshold_maybe=None,
                             threshold_no=None,
                             distance_weight=1,
                             decision_weight=1)

        self.calibrator_conf.Acceptable_false_negative_rate = 0.9
        self.calibrator_conf.thre_upper_at_most_xpercent_FNR = 0.9
        self.calibrator_conf.Minimum_true_negative_rate = 0.1
        self.calibrator_conf.thre_below_at_least_xpercent_TNR = 0.1

        out_conf = self.calibrator_conf.export_to_Algo(tmp_conf)
        self.assertEqual(out_conf.threshold_yes_to_maybe, 0.1)
        self.assertEqual(out_conf.threshold_maybe_to_no, 0.9)


if __name__ == '__main__':
    unittest.main()
