# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.pardir))
import common.TestDBHandler.test_instance_launcher as test_database_handler
from common.environment_variable import get_homedir

import pathlib
import unittest
import time


class test_tests_database_launcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")

        self.test_db_handler = test_database_handler.TestInstanceLauncher()
        db_test_conf = test_database_handler.TestInstance_database_conf()
        print("\n[TESTS] LAUNCHING DATABASE AS TEST : NOTHING WILL BE WRITEN ON STORAGE OR CACHE DATABASES [TESTS]\n")
        self.test_db_handler.create_full_instance(db_conf=db_test_conf)

    def tearDown(self):
        print("\n[TESTS] STOPPING DATABASE AS TEST : NOTHING WILL BE REMOVED ON STORAGE OR CACHE DATABASES [TESTS]\n")
        self.test_db_handler.tearDown()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)
        print("\n\nRUNNNING HERE\n\n")

    def test_correct_test_db_launch(self):
        time.sleep(6)
        print("\n\nRUNNNING HERE\n\n")
        self.assertTrue((get_homedir() / "carlhauser_server" / "Data" / "database_sockets" / "test.sock").exists())
        self.assertTrue(not (get_homedir() / "carlhauser_server" / "Data" / "database_sockets" / "cache.sock").exists())
        self.assertTrue(not (get_homedir() / "carlhauser_server" / "Data" / "database_sockets" / "storage.sock").exists())
        time.sleep(6)

if __name__ == '__main__':
    unittest.main()
