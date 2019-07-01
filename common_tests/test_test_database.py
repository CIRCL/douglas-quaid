# -*- coding: utf-8 -*-

import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server_tests.context import *
import common.TestDBHandler.test_database_handler as test_database_handler
import pathlib
import unittest
import time

class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")

        self.test_db_handler = test_database_handler.TestDatabaseHandler()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_correct_test_db_launch(self):
        test_configuration = test_database_handler.Test_database_conf()

        self.test_db_handler.setUp(db_conf=test_configuration)

        time.sleep(6)
        print("RUNNNING HERE")
        time.sleep(6)

        self.test_db_handler.tearDown()


if __name__ == '__main__':
    unittest.main()