# -*- coding: utf-8 -*-

import unittest

import cv2
import numpy as np

import carlhauser_server.Helpers.pickle_import_export as pickle_import_export

import logging
import pathlib

from carlhauser_server.Helpers.environment_variable import get_homedir
class testPICKLEImportExport(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/pickle_import_export")

    def test_absolute_truth_and_meaning(self):
        assert True

    '''
    def test_pickle_export(self):
        # Test picture export function
        a = np.arange(15).reshape(3, 5)
        b = np.array( [[ True, True, True, False ], [ True, False, False, False ]] )
        obj = {"test_array":a, "values_bool":b}
        try :
                pc = pickle_import_export.get_pickle_from_object(obj)
                self.assertTrue(True)
        except Exception as e:
                self.assertTrue(False)

    def test_pickle_import(self):
        # Test picture import functions
        a = np.arange(15).reshape(3, 5)
        b = np.array( [[ True, True, True, False ], [ True, False, False, False ]] )
        try :
                pickle_import_export.get_object_from_pickle(img.read(), self.test_file_path / "output_1.bmp")
                self.assertTrue(True)
        except Exception as e:
                self.assertTrue(False)
    '''

    def test_pickle_import_export_consistency(self):
        a = np.arange(15).reshape(3, 5)
        b = np.array([[True, True, True, False], [True, False, False, False]])
        obj = {"test_array": a, "values_bool": b}
        pickler = pickle_import_export.Pickler()
        # Test consistency between import and export function
        self.logger.debug("Save to pickle ... ")
        pc = pickler.get_pickle_from_object(obj)
        self.logger.debug("Load from pickle ... ")
        obj2 = pickler.get_object_from_pickle(pc)

        self.logger.info(f"Original object : {obj}")
        self.logger.info(f"Retrieved object : {obj2}")
        self.assertEqual(len(obj2), len(obj))
        self.assertEqual(type(obj2), type(obj))
        self.assertEqual(type(obj2["test_array"]), type(obj["test_array"]))
        self.assertEqual(len(obj2["test_array"]), len(obj["test_array"]))
        self.assertEqual(type(obj2["values_bool"]), type(obj["values_bool"]))
        self.assertEqual(len(obj2["values_bool"]), len(obj["values_bool"]))

    def test_pickle_import_export_ORB(self):
        algo = cv2.ORB_create(nfeatures=10)
        img = cv2.imread(str(self.test_file_path / "original.bmp"), 0)

        # compute the descriptors with ORB
        kp, des = algo.detectAndCompute(img, None)

        self.logger.debug(f"Keypoints : {kp}")
        self.logger.debug(f"Example of Keypoint")

        pickler = pickle_import_export.Pickler()
        self.logger.debug("Save to pickle ... ")
        pc = pickler.get_pickle_from_object(kp)
        self.logger.debug("Load from pickle ... ")
        kp2 = pickler.get_object_from_pickle(pc)

        for i, k in enumerate(kp):
            self.assertEqual(kp[i].response, kp2[i].response)
            self.assertEqual(kp[i].angle, kp2[i].angle)
            self.assertEqual(kp[i].class_id, kp2[i].class_id)
            self.assertEqual(kp[i].octave, kp2[i].octave)
            self.assertEqual(kp[i].pt, kp2[i].pt)
            self.assertEqual(kp[i].size, kp2[i].size)


if __name__ == '__main__':
    unittest.main()
