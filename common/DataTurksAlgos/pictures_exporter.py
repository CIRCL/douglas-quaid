#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pathlib
from pprint import pformat
from shutil import copyfile
from typing import List, Dict

import common.ImportExport.json_import_export as json_io
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


def dir_path(path):
    if pathlib.Path(path).exists():
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


class PicturesExporter:
    def __init__(self):
        self.logger = logging.getLogger()
        self.dataturks: pathlib.Path = None
        self.dataturks_json: Dict = None
        self.src_folder: pathlib.Path = None
        self.dst_folder: pathlib.Path = None
        self.already_copied: pathlib.Path = None
        self.packet_size: int = None

        # Internal
        self.pic_to_path: Dict = {}
        self.pic_already_to_path: Dict = {}
        self.dict_to_export: List[Dict] = [{}]

    def launch_copy(self):
        self.load_dataturks_json()
        self.load_pictures_to_copy()
        self.load_pictures_to_not_copy()

        self.iterate_over_dataturks_json()
        self.export_dicts()

    # ===================== UTILITIES =====================

    def load_dataturks_json(self):
        self.dataturks_json = json_io.load_json(self.dataturks)

    @staticmethod
    def load_files(path: pathlib.Path) -> List[pathlib.Path]:
        path = path.resolve()
        p = path.resolve().glob('**/*')
        files = [x for x in p if x.is_file()]

        files.sort()  # To prevent System's way of sorting paths.
        # Therefore, we are sure about the order of treatment on any machine (determinism)

        return files

    @staticmethod
    def list_to_dict(files_list: List[pathlib.Path]) -> Dict[str, pathlib.Path]:
        tmp_dict: Dict[str, pathlib.Path] = {}

        for f in files_list:
            tmp_dict[f.name] = f

        return tmp_dict

    def load_pictures_to_copy(self):
        file_list = self.load_files(self.src_folder)
        self.pic_to_path = self.list_to_dict(file_list)

    def load_pictures_to_not_copy(self):
        file_list = self.load_files(self.dst_folder)
        already_copied_files = self.load_files(self.already_copied)

        self.pic_already_to_path = {**self.list_to_dict(file_list), **self.list_to_dict(already_copied_files)}

    def iterate_over_dataturks_json(self):

        nb_of_element = 0
        deleted = 0
        not_found = 0
        entry_number = 0
        no_label = 0
        copied = 0
        basename = "folder_"

        for element in self.dataturks_json:
            entry_number += 1
            # self.logger.debug(f"Current element : \n{pformat(element)}")

            # Do delete = we jump
            try:
                annotations = element["annotation"]
                labels = annotations["labels"]
            except Exception as e:
                self.logger.error(f"Error when labels fetching from {pformat(element)} : {e}")
                no_label += 1
                continue

            if "to_delete" in labels:
                deleted += 1
                self.logger.error(f"To Delete picture detected {pformat(element)} not copied !")
                continue

            tmp_path = pathlib.Path(element["content"])

            # Path already copied previously = we jump
            if tmp_path.name in self.pic_already_to_path:
                continue

            # File seems good.
            pack_id = nb_of_element // self.packet_size

            # Save labels in a corner for later export
            if pack_id + 1 != len(self.dict_to_export):
                # We don't have enough dictionnary, we add one
                self.dict_to_export.append({})

            self.dict_to_export[pack_id][tmp_path.name] = labels

            # Generate new path where to be saved
            curr_folder_name = basename + str(pack_id)
            nb_of_element += 1
            curr_saving_path = self.dst_folder / curr_folder_name
            curr_saving_path.mkdir(exist_ok=True)

            # We copy the file
            if self.pic_to_path.get(tmp_path.name, None) is not None:
                src = str(self.pic_to_path[tmp_path.name])
                dst = str(curr_saving_path / tmp_path.name)
                self.logger.info(f"Picture {src} copied to {dst}")
                copyfile(src, dst)
                copied += 1
            else:
                not_found += 1
                self.logger.critical(f"Picture not found as file on the disk ! {tmp_path.name}")

        self.logger.info(f"Pictures deleted = {deleted}")
        self.logger.info(f"Pictures not found = {not_found}")
        self.logger.info(f"Pictures in total in original file = {entry_number}")
        self.logger.info(f"Pictures without label = {no_label}")
        self.logger.info(f"Pictures copied = {copied}")

    def export_dicts(self):
        for i, curr_dict in enumerate(self.dict_to_export):
            json_io.save_json(curr_dict, self.dst_folder / ("labels_" + str(i) + ".json"))


'''
  {
    "content": "http://149.13.33.83:80/img/97/abrupt-ratty-normal-stupid.png",
    "annotation": {
      "labels": [
        "dark-web:topic=\"legitimate\"",
        "dark-web:motivation=\"education-training\""
      ],
      "note": ""
    },
    "extras": null,
    "metadata": {
      "first_done_at": 1560523602000,
      "last_updated_at": 1560523602000,
      "sec_taken": 0,
      "last_updated_by": "zettacircl@protonmail.com",
      "status": "done",
      "evaluation": "NONE"
    }
  },
  {
    "content": "http://149.13.33.83:80/img/dc/striped-lively-opposite-strike.png",
    "annotation": {
      "labels": [
        "dark-web:topic=\"drugs-narcotics\"",
        "dark-web:topic=\"search-engine-index\"",
        "to_delete"
      ],
      "note": ""
    },
    "extras": null,
    "metadata": {
      "first_done_at": 1561467239000,
      "last_updated_at": 1561467239000,
      "sec_taken": 0,
      "last_updated_by": "zettacircl@protonmail.com",
      "status": "done",
      "evaluation": "NONE"
    }
  },
'''

# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    # Use :
    # First time : python3 ./pictures_exporter.py -s ./../SOURCE -d ./../DEST -p 4000
    # Next time : python3 ./pictures_exporter.py -s ./../SOURCE -d ./../DEST -p 4000 -p ./../ALREADY_DONE
    parser = argparse.ArgumentParser(description='Export pictures from dataturks json to a new folder')
    parser.add_argument("-i", '--dataturks_json', dest="dataturks", type=dir_path, help='Json exported from dataturks')
    parser.add_argument("-s", '--source_folder', dest="src", type=dir_path, help='Source folder where all pictures are')
    parser.add_argument("-d", '--destination_folder', dest="dest", type=dir_path, help='Destination folder where all pictures will be copied')
    parser.add_argument("-a", '--already_copied_folder', dest="already", type=dir_path, help='Folder where pictures were already copied, and we want to jump them')
    parser.add_argument("-p", '--packet_size', dest="packet", type=int, help='Number of picture to put in the packet')
    args = parser.parse_args()

    # Load the provided configuration file and create back the Configuration Object
    dt_exporter = PicturesExporter()

    dt_exporter.dataturks = pathlib.Path(args.dataturks)
    dt_exporter.src_folder = pathlib.Path(args.src)
    dt_exporter.dst_folder = pathlib.Path(args.dest)
    dt_exporter.already_copied = pathlib.Path(args.already) if args.already is not None else None
    dt_exporter.packet_size = args.packet

    dt_exporter.launch_copy()

# export PYTHONPATH="${PYTHONPATH}:/home/vincent/douglas-quaid/"
# export CARLHAUSER_HOME="/home/vincent/douglas-quaid"
# python3 ./pictures_exporter.py -s ./../../../AIL_dataset_checked/ -d ./../../../PACKS/ -i ./../../../AIL4000.json -p 4000
