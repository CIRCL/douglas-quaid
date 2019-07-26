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

        l = [10, 50, 100, 500, 1000, 5000, 10000]
        self.assertListEqual(l, list_boxes)

    def test_generate_boxes_linear(self):
        list_boxes = self.scalability_conf.generate_boxes_linear(10000)

        self.logger.info("List boxes generated : ")
        self.logger.info(list_boxes)

        l = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700, 720, 740, 760,
             780, 800, 820, 840, 860, 880, 900, 920, 940, 960, 980, 1000, 1020, 1040, 1060, 1080, 1100, 1120, 1140, 1160, 1180, 1200, 1220, 1240, 1260, 1280, 1300, 1320, 1340, 1360, 1380, 1400, 1420,
             1440, 1460, 1480, 1500, 1520, 1540, 1560, 1580, 1600, 1620, 1640, 1660, 1680, 1700, 1720, 1740, 1760, 1780, 1800, 1820, 1840, 1860, 1880, 1900, 1920, 1940, 1960, 1980, 2000]
        self.assertListEqual(l, list_boxes)


if __name__ == '__main__':
    unittest.main()
