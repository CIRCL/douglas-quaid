#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import json
import pathlib
from typing import Dict
from common.ImportExport.json_import_export import save_json


class Referencer:

    def __init__(self):
        self.already_generated = {}

    def reference_all_files(self, path: pathlib.Path):
        path = path.resolve()
        p = path.resolve().glob('**/*')
        files = [x for x in p if x.is_file()]

        files.sort()  # To prevent System's way of sorting paths.
        # Therefore, we are sure about the order of treatment on any machine (determinism)

        for f in files:
            self.check_correctness(f.name)
            tmp_file = f.read_bytes()
            hash_list = self.hash_file(tmp_file)
            self.store_hash(f.name, hash_list)

        save_json(self.already_generated, path.parent / (str(path.name) + "_references.json"))

        print(f"Done. {len(files)} hashed and stored in.")

    @staticmethod
    def check_correctness(name:str):
        if " " in name :
            print("WARNING : space detected in namespace. Are you sure you renamed file correctly ?")

    @staticmethod
    def hash_file(open_file) -> Dict:
        hash_list = {}

        hash_list['md5'] = hashlib.md5(open_file).hexdigest()
        hash_list['sha1'] = hashlib.sha1(open_file).hexdigest()
        hash_list['sha256'] = hashlib.sha256(open_file).hexdigest()

        return hash_list

    def store_hash(self, name: str, hash_list):
        self.already_generated[name] = hash_list


def main():
    # Usage example : python3 ./referencer.py -p ./MINI_DATASET/
    parser = argparse.ArgumentParser(description='Hash all files in the given directory and subdirectories, and saves a summary in a <Foldername>_references.json> at same level as target folder.')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), default=1, help='all path')
    parser.add_argument('--version', action='version', version='humanizer %s' % "1.0.0")

    args = parser.parse_args()
    referencer = Referencer()
    referencer.reference_all_files(args.path)


if __name__ == "__main__":
    main()
