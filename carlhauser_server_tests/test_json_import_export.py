# -*- coding: utf-8 -*-

import unittest

import carlhauser_server.Helpers.json_import_export as json_import_export
import logging
import pathlib
from carlhauser_server.Helpers.environment_variable import get_homedir

class testJSONImportExport(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / pathlib.Path("carlhauser_server_tests/test_Helpers/json_import_export")

        self.simple_object = {"myobjectname": "ThisIsMyObject",
                              "MyObjectList": ["value1", "value2", "value3", "value4"]}
        self.path_object = {"myobjectname": "ThisIsMyObject",
                            "MyObjectList": ["value1", "value2", "value3", "value4"],
                            "Path": pathlib.Path("/My/Path/")}

    def tearDown(self):

        outputs = [(self.test_file_path / "export_test.json")]

        # Delete all created files
        for path in outputs:
            if path.exists():
                path.unlink()

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_json_export(self):
        # Test json export function
        try:
            json_import_export.save_json(self.simple_object, self.test_file_path / "export_test.json")
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

        try:
            json_import_export.save_json(self.path_object, self.test_file_path / "export_test.json")
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

    def test_json_import(self):
        # Test json import functions
        try:
            obj = json_import_export.load_json(self.test_file_path / "does_not_exist.json")
            self.assertTrue(False)
        except Exception as e:
            self.assertTrue(True)

        try:
            obj = json_import_export.load_json(self.test_file_path / "path_object.json")
            # Verify if object is correct
            self.assertEqual(obj["myobjectname"], "ThisIsMyObject")
            self.assertEqual(obj["MyObjectList"][1], "value2")
            self.assertEqual(obj["Path"], "/My/Path")
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

    def test_json_import_export_consistency(self):
        # Test consistency between import and export function

        try:
            json_import_export.save_json(self.simple_object, self.test_file_path / "export_test.json")
            obj = json_import_export.load_json(self.test_file_path / "export_test.json")

            self.assertEqual(self.simple_object, obj)
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

        try:
            json_import_export.save_json(self.path_object, self.test_file_path / "export_test.json")
            obj = json_import_export.load_json(self.test_file_path / "export_test.json")

            # TODO : Create pathlib.Path from string path. For not, can't be equal
            self.assertNotEqual(self.path_object, obj)
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

        return


if __name__ == '__main__':
    unittest.main()
