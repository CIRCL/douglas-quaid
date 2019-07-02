# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
from common.Calibrator.Calibrator import Calibrator

import unittest


class test_calibrator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        # self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")
        self.calibrator_instance = Calibrator()

        self.micro_dataset_input_path = get_homedir() / "common_tests" / "Calibrator_tests" / "MINI_DATASET"
        self.micro_dataset_gt_path = get_homedir() / "common_tests" / "Calibrator_tests" / "MINI_DATASET_VISJS.json"
        self.micro_dataset_output_path = get_homedir() / "common_tests" / "Calibrator_tests" / "OUTPUT"

    def tearDown(self):
        pass

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_calibrator_launch(self):
        self.logger.debug("Launching calibration... (tests)")
        self.calibrator_instance.calibrate_douglas_quaid(folder_of_pictures=self.micro_dataset_input_path,
                                                         ground_truth_file=self.micro_dataset_gt_path,
                                                         output_folder=self.micro_dataset_output_path)


if __name__ == '__main__':
    unittest.main()
