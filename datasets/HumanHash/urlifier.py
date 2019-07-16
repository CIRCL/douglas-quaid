#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import pathlib


class Referencer:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.already_generated = set({})

    def reference_all_files(self, path: pathlib.Path):
        path = path.resolve()
        p = path.resolve().glob('**/*')
        files = [x for x in p if x.is_file()]

        files.sort()  # To prevent System's way of sorting paths.
        # Therefore, we are sure about the order of treatment on any machine (determinism)

        for f in files:
            self.store_value(f, path)

        save_path = path.parent / (str(path.name) + '_url_list.txt')
        self.save_to_text(list(self.already_generated), save_path)

        print(f"Done. {len(files)} converted in url and stored in {save_path}.")

    @staticmethod
    def check_correctness(name: str):
        if " " in name:
            print("WARNING : space detected in namespace. Are you sure you renamed file correctly ?")

    def store_value(self, name: pathlib.Path, reference_path):
        tmp_str = "http://" + str(self.ip) + ":" + str(self.port) + "/" + str(name.relative_to(reference_path))
        self.already_generated.add(tmp_str)

    @staticmethod
    def save_json(obj, file_path: pathlib.Path):
        # Create parents if they does not exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=4)

        print(f"File saved as {file_path}.")

    @staticmethod
    def save_to_text(obj, file_path: pathlib.Path):
        with open(str(file_path), 'w') as f:
            for item in obj:
                f.write("%s\n" % item)


def main():
    # Usage example : python3 ./referencer.py -p ./MINI_DATASET/
    parser = argparse.ArgumentParser(description='Hash all files in the given directory and subdirectories, and saves a summary in a <Foldername>_references.json> at same level as target folder.')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), default=1, help='all path')
    parser.add_argument('-i', '--ip', dest='ip', action='store', type=str, default=1, help='IP of the server to serve')
    parser.add_argument('-t', '--port', dest='port', action='store', type=str, default=1, help='port of the server to serve')
    parser.add_argument('--version', action='version', version='humanizer %s' % "1.0.0")

    args = parser.parse_args()
    referencer = Referencer(args.ip, args.port)
    referencer.reference_all_files(args.path)


if __name__ == "__main__":
    main()
