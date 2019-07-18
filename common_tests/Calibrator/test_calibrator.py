# -*- coding: utf-8 -*-

import logging
import pprint
import unittest

import common.Calibrator.calibrator_conf as calibrator_conf
from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.Calibrator.threshold_calibrator import Calibrator
from common.ImportExport.json_import_export import Custom_JSON_Encoder
from common.environment_variable import get_homedir


class test_calibrator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = configuration.Default_configuration()
        # self.test_file_path = pathlib.Path.cwd() / pathlib.Path("tests/test_files")
        self.calibrator_instance = Calibrator()

        self.micro_dataset_input_path = get_homedir() / "common_tests" / "Calibrator" / "Calibrator_tests" / "MICRO_DATASET"
        self.micro_dataset_gt_path = get_homedir() / "common_tests" / "Calibrator" / "Calibrator_tests" / "MICRO_DATASET_VISJS.json"
        self.micro_dataset_output_path = get_homedir() / "common_tests" / "Calibrator" / "Calibrator_tests" / "OUTPUT"

    def tearDown(self):
        pass

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_calibrator_launch(self):
        self.logger.debug("Launching calibration... (tests)")
        new_calibrator_conf = calibrator_conf.Default_calibrator_conf()

        new_calibrator_conf.Minimum_true_negative_rate = 0.9
        new_calibrator_conf.Minimum_true_positive_rate = 0.9

        self.calibrator_instance.set_calibrator_conf(tmp_calibrator_conf=new_calibrator_conf)
        list_algos = self.calibrator_instance.calibrate_douglas_quaid(folder_of_pictures=self.micro_dataset_input_path,
                                                                      ground_truth_file=self.micro_dataset_gt_path,
                                                                      output_folder=self.micro_dataset_output_path)
        for algo in list_algos:
            self.assertTrue(algo.threshold_yes_to_maybe <= algo.threshold_maybe_to_no)

    def test_feature_conf_generator(self):
        self.logger.debug("Launching calibration... (tests)")

        # A_HASH
        tmp_algo_conf = Algo_conf("A_HASH", is_enabled=True, threshold_maybe=0.2, threshold_no=0.6, distance_weight=1, decision_weight=1)
        print("tmp_algo_conf", tmp_algo_conf)

        fe_conf_modified = self.calibrator_instance.generate_feature_conf(tmp_algo_conf)

        print("fe_conf_modified", fe_conf_modified)
        json_encoder = Custom_JSON_Encoder()
        self.logger.debug(f"Registered configuration files are ... ")
        self.logger.debug(f"Configuration fe_conf_modified : \n{pprint.pformat(json_encoder.encode(fe_conf_modified))}")

        self.assertTrue(fe_conf_modified.A_HASH.is_enabled)
        self.assertTrue(fe_conf_modified.list_algos[0].is_enabled)
        self.assertFalse(fe_conf_modified.P_HASH.is_enabled)
        self.assertFalse(fe_conf_modified.ORB.is_enabled)
        self.assertFalse(fe_conf_modified.D_HASH.is_enabled)
        self.assertFalse(fe_conf_modified.list_algos[2].is_enabled)
        self.assertFalse(fe_conf_modified.list_algos[5].is_enabled)
        self.assertFalse(fe_conf_modified.list_algos[4].is_enabled)

        # ORB
        tmp_algo_conf = Algo_conf("ORB", is_enabled=True, threshold_maybe=0.2, threshold_no=0.6, distance_weight=1, decision_weight=1)
        print("tmp_algo_conf", tmp_algo_conf)
        fe_conf_modified = self.calibrator_instance.generate_feature_conf(tmp_algo_conf)

        print("fe_conf_modified", fe_conf_modified)
        json_encoder = Custom_JSON_Encoder()
        self.logger.debug(f"Registered configuration files are ... ")
        self.logger.debug(f"Configuration fe_conf_modified : \n{pprint.pformat(json_encoder.encode(fe_conf_modified))}")

        self.assertTrue(fe_conf_modified.ORB.is_enabled)
        self.assertTrue(fe_conf_modified.list_algos[7].is_enabled)
        self.assertFalse(fe_conf_modified.P_HASH.is_enabled)
        self.assertFalse(fe_conf_modified.A_HASH.is_enabled)
        self.assertFalse(fe_conf_modified.D_HASH.is_enabled)
        self.assertFalse(fe_conf_modified.list_algos[2].is_enabled)
        self.assertFalse(fe_conf_modified.list_algos[5].is_enabled)
        self.assertFalse(fe_conf_modified.list_algos[4].is_enabled)


if __name__ == '__main__':
    unittest.main()
