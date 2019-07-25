# -*- coding: utf-8 -*-

import logging
import unittest

from common.Scalability_evaluator.scalability_conf import Default_scalability_conf


class test_scalability_conf(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        self.scalability_conf = Default_scalability_conf()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_generate_boxes(self):

        list_boxes = self.scalability_conf.generate_boxes(10000)

        self.logger.info("List boxes generated : ")
        self.logger.info(list_boxes)

        l =[10, 50, 100, 500, 1000, 5000, 10000]
        self.assertListEqual(l, list_boxes)


if __name__ == '__main__':
    unittest.main()
