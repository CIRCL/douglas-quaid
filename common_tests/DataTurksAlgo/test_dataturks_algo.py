# -*- coding: utf-8 -*-

import logging
import pathlib
import unittest
from shutil import rmtree

from common.DataTurksAlgos.pictures_exporter import PicturesExporter
from common.ImportExport.json_import_export import load_json
from common.environment_variable import get_homedir


class test_template(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        self.base_folder = get_homedir() / "datasets" / "douglas-quaid-tests" / "DataTurks_tests"

    @staticmethod
    def create_sorted(base_path: pathlib.Path) -> PicturesExporter:
        """
        Load the provided configuration file and create back the Configuration Object
        :return: Nothing
        """

        dt_exporter = PicturesExporter()

        dt_exporter.dataturks = pathlib.Path(base_path / "ail.json")
        dt_exporter.src_folder = pathlib.Path(base_path / "input")
        dt_exporter.dst_folder = pathlib.Path(base_path / "output")
        dt_exporter.already_copied = pathlib.Path(base_path / "already_copied")
        dt_exporter.packet_size = 10

        return dt_exporter

    def clean_folder(self, base_path: pathlib.Path):
        tmp_output = pathlib.Path(base_path / "output")

        for f in tmp_output.iterdir():
            if f.is_dir():
                self.logger.debug(f"Removing folder : {f}")
                rmtree(f)
            if f.is_file():
                self.logger.debug(f"Removing file : {f}")
                f.unlink()

    def check_size_folder(self, folder: pathlib.Path, size: int):
        self.logger.debug(f"Checking size of folder {folder.name}")
        nb_files_first_folder = len(list(folder.glob('*')))
        self.assertEqual(nb_files_first_folder, size)

    def test_first_copy_packets_size(self):
        test_path = self.base_folder / "test_0"

        self.clean_folder(test_path)
        dt_exporter = self.create_sorted(test_path)

        dt_exporter.launch_copy()

        self.check_size_folder(test_path / "output" / "folder_0", 10)
        self.check_size_folder(test_path / "output" / "folder_1", 5)

        labels_0 = load_json(test_path / "output" / "labels_0.json")
        self.assertEqual(len(labels_0), 10)
        labels_1 = load_json(test_path / "output" / "labels_1.json")
        self.assertEqual(len(labels_1), 5)

    def test_already_copied_not_recopied(self):
        test_path = self.base_folder / "test_1"

        self.clean_folder(test_path)
        dt_exporter = self.create_sorted(test_path)

        dt_exporter.launch_copy()

        self.check_size_folder(test_path / "output" / "folder_0", 10)
        self.check_size_folder(test_path / "output" / "folder_1", 2)

        labels_0 = load_json(test_path / "output" / "labels_0.json")
        self.assertEqual(len(labels_0), 10)
        labels_1 = load_json(test_path / "output" / "labels_1.json")
        self.assertEqual(len(labels_1), 2)

    def test_to_delete(self):
        test_path = self.base_folder / "test_2"

        self.clean_folder(test_path)
        dt_exporter = self.create_sorted(test_path)

        dt_exporter.launch_copy()

        self.check_size_folder(test_path / "output" / "folder_0", 10)
        self.assertFalse((test_path / "output" / "folder_1").exists())

        labels_0 = load_json(test_path / "output" / "labels_0.json")
        self.assertEqual(len(labels_0), 10)
        for i in labels_0.values():
            self.assertFalse(i[0] == "to_delete")
        self.assertFalse((test_path / "output" / "labels_1.json").exists())
