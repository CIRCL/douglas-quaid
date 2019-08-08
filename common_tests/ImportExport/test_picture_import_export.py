# -*- coding: utf-8 -*-

import unittest

import common.ImportExport.picture_import_export as picture_import_export
import logging
import pathlib

from common.environment_variable import get_homedir

class testPICTUREImportExport(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.test_file_path = get_homedir() / "datasets" / "TEST_DATASETS" / "picture_import_export"

    def tearDown(self):

        outputs = [(self.test_file_path / "output_1.bmp"),
                   (self.test_file_path / "output_2.bmp"), ]

        # Delete all created files
        for path in outputs:
            if path.exists():
                path.unlink()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    def test_picture_export(self):
        # Test picture export function

        with open(str(self.test_file_path / "original.bmp"), 'rb') as img:
            try:
                picture_import_export.save_picture(img.read(), self.test_file_path / "output_1.bmp")
                self.assertTrue(True)
            except Exception as e:
                self.assertTrue(False)

    def test_picture_import(self):
        # Test picture import functions

        with open(str(self.test_file_path / "original.bmp"), 'rb') as img:
            try:
                obj = picture_import_export.load_picture(self.test_file_path / "original.bmp")
                self.assertEqual(obj, img.read())
                self.assertTrue(True)
            except Exception as e:
                self.assertTrue(False)

    def test_picture_import_export_consistency(self):
        # Test consistency between import and export function
        print("Load picture ... ")
        obj = picture_import_export.load_picture(self.test_file_path / "original.bmp")
        print("Save picture ... ")
        picture_import_export.save_picture(obj, self.test_file_path / "output_1.bmp")

        return


if __name__ == '__main__':
    unittest.main()
