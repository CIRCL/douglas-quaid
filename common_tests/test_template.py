# -*- coding: utf-8 -*-

import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server_tests.context import *
import pathlib
import unittest

class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")

    def test_absolute_truth_and_meaning(self):
        assert True


if __name__ == '__main__':
    unittest.main()