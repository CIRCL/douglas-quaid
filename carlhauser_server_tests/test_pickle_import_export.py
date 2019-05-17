# -*- coding: utf-8 -*-
from carlhauser_server_tests.context import *
from PIL import Image

import carlhauser_server.Helpers.pickle_import_export as pickle_import_export

import unittest
import numpy as np

class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/picture_import_export")

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
        b = np.array( [[ True, True, True, False ], [ True, False, False, False ]] )
        obj = {"test_array":a, "values_bool":b}

        # Test consistency between import and export function
        print("Save to pickle ... ")
        pc = pickle_import_export.get_pickle_from_object(obj)
        print("Load from pickle ... ")
        obj2 = pickle_import_export.get_object_from_pickle(pc)

        self.logger.info(f"Original object : {obj}")
        self.logger.info(f"Retrieved object : {obj2}")
        self.assertEqual(len(obj2),len(obj))
        self.assertEqual(type(obj2),type(obj))
        self.assertEqual(type(obj2["test_array"]),type(obj["test_array"]))
        self.assertEqual(len(obj2["test_array"]),len(obj["test_array"]))
        self.assertEqual(type(obj2["values_bool"]),type(obj["values_bool"]))
        self.assertEqual(len(obj2["values_bool"]),len(obj["values_bool"]))


if __name__ == '__main__':
    unittest.main()
