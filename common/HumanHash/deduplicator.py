#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import pathlib
import shutil
from pprint import pformat
from typing import Dict, Set


class Deduplicator:

    def __init__(self):
        self.already_generated = set({})

    def deduplicate_folder_to(self, path: pathlib.Path, output_path: pathlib.Path):

        if not output_path.resolve().exists():
            output_path.resolve().mkdir(exist_ok=True)

        p = path.resolve().glob('**/*')
        files = [x for x in p if x.is_file()]

        tmp_leng = len(files)
        files.sort()  # To prevent System's way of sorting paths.
        # Therefore, we are sure about the order of treatment on any machine (determinism)
        tmp_leng_after = len(files)

        if tmp_leng != tmp_leng_after:
            raise Exception("Sorting removed files ! Aborting.")

        set_dict: Dict[str, Set[pathlib.Path]] = {}

        for i, file in enumerate(files):
            # Open file
            with open(str(file), "rb") as f:
                if i % 20 == 0 :
                    print(f"Hashing {f.name} and 20 other")

                tmp_bytes = f.read()  # read entire file as bytes

                # compute sha1
                sha256 = self.get_hash(tmp_bytes)

                # Store file path in a mapping sha256 -> all file paths
                if sha256 not in set_dict:
                    set_dict[sha256] = {file}
                else:
                    set_dict[sha256].add(file)

        print(f"Current mapping {pformat(set_dict)}. Continue ? ")
        print(f"Current number of files in folder : {len(files)}")

        input()

        nb_remove = 0

        for s in set_dict.values():

            if len(s) > 1:
                print(f"Current mapping {s} show duplicates. Saving one of these picture.")
                to_keep = s.pop()
                nb_remove += len(s)

                # We remove one from the mapping
                print(f"Would you like to remove {s} and keep {to_keep} ? ")
                shutil.copy(str(to_keep), str(output_path / str(to_keep.name)))
            else:
                print(f"Current mapping {s} show no duplicate. Saving unique picture.")
                to_keep = s.pop()
                shutil.copy(str(to_keep), str(output_path / str(to_keep.name)))

        print(f"Number of files in original folder : {len(files)}")
        print(f"Done. {nb_remove} duplicated files not copied.")
        print(f"Done. {len(files) - nb_remove} not duplicated files copied.")

    @staticmethod
    def get_hash(content) -> str:
        return hashlib.sha256(content).hexdigest()


def main():
    # Usage example : python3 ./deduplicator.py -p ./../../../DATASETS/PHISHING/PHISHING-DATASET-SORTED/ -o ./../../../DATASETS/PHISHING/PHISHING-DATASET-SORTED-DEDUPLICATED/
    parser = argparse.ArgumentParser(description='Check all files in the given directory and subdirectory for duplicates (strict, by hash) and remove them upon validation')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), help='input path')
    parser.add_argument('-o', '--outpath', dest='outpath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='output path')
    parser.add_argument('--version', action='version', version='deduplicator %s' % "1.0.0")

    args = parser.parse_args()
    deduplicator = Deduplicator()
    deduplicator.deduplicate_folder_to(args.path, args.outpath)


def test():
    deduplicator = Deduplicator()


if __name__ == "__main__":
    main()
