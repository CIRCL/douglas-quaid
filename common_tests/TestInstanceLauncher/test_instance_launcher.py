# -*- coding: utf-8 -*-

import logging

import pathlib
import unittest


class test_tests_database_launcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)
        print("\n\nRUNNNING HERE\n\n")

    def test_compute_score_for_one_threshold(self):
        pass


if __name__ == '__main__':
    unittest.main()
