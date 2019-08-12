# -*- coding: utf-8 -*-

import logging
import unittest

from common.Scalability_evaluator.scalability_evaluator import ScalabilityEvaluator


class test_scalability_conf(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        self.scalability_eval = ScalabilityEvaluator()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_biner(self):
        potential_pictures = {str(i) for i in range(0, 35)}
        potential_pictures, bin_set = self.scalability_eval.biner(potential_pictures, 10)

        self.logger.info(potential_pictures)
        self.logger.info(bin_set)
        self.assertEqual(len(bin_set), 10)
        self.assertEqual(len(potential_pictures), 25)

        potential_pictures, bin_set = self.scalability_eval.biner(potential_pictures, 10)
        self.logger.info(bin_set)
        self.assertEqual(len(bin_set), 10)
        self.assertEqual(len(potential_pictures), 15)

        potential_pictures, bin_set = self.scalability_eval.biner(potential_pictures, 10)
        self.logger.info(bin_set)
        self.assertEqual(len(bin_set), 10)
        self.assertEqual(len(potential_pictures), 5)

        potential_pictures, bin_set = self.scalability_eval.biner(potential_pictures, 10)
        self.logger.info(bin_set)
        self.assertEqual(len(bin_set), 5)
        self.assertEqual(len(potential_pictures), 0)


if __name__ == '__main__':
    unittest.main()
