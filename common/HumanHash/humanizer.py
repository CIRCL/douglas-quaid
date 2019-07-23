#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# PLEASE BE AWARE THIS IMPORT IS NOT IN THE PIPENV.
# THIS IS NOT A DEPENDENCY AS IT IS NOT REQUIRED STRICTLY TO RUN THE LIBRARY.
# PLEASE INSTALL BY YOURSELF IF YOU NEED TO RUN THIS SCRIPT !
# Please see : https://pypi.org/project/codenamize/ and https://github.com/jjmontesl/codenamize
import argparse
import hashlib
import pathlib
import pprint
import shutil

from codenamize import codenamize

'''
COLLISIONS CALCULATIONS
3 adj (max 4 chars) = 962286000 combinations
3 adj (max 5 chars) = 25471468750 combinations
3 adj (max 6 chars) = 122636229513 combinations
3 adj (max 7 chars) = 355283372136 combinations
3 adj (max 0 chars) = 2119641566400 combinations <= We choose this configuration :)
TESTS
  (*, 1 adj, max 3) => 1742 distinct results (space size is 2760)
  (*, 2 adj, max 3) => 41855 distinct results (space size is 66240)
  (*, 3 adj, max 3) => 1005353 distinct results (space size is 1589760)

'''


class Humanizer:

    def __init__(self):
        self.already_generated = set({})

    def rename_all_files(self, path: pathlib.Path, output_path: pathlib.Path):
        p = path.resolve().glob('**/*')
        files = [x for x in p if x.is_file()]

        tmp_leng = len(files)
        files.sort()  # To prevent System's way of sorting paths.
        # Therefore, we are sure about the order of treatment on any machine (determinism)
        tmp_leng_after = len(files)

        if tmp_leng != tmp_leng_after:
            raise Exception("Sorting removed files ! Aborting.")

        for f in files:
            print(f"Adding {f.name} to already seen file name list.")
            self.already_generated.add(f.name)  # toto.png
        input()

        print(f"Going to change names of : {pprint.pformat(files)} \n Are you sure you want to continue ?")
        input()

        first = True
        for file in files:

            with open(str(file), "rb") as f:
                bytes = f.read()  # read entire file as bytes

                new_name = self.humanize_name(bytes, file.name, file.suffix)  # toto.png ->  tata.png

                if first:
                    print(f"The file {file.name} is going to be changed to {new_name}. \n Do you want to continue ? (Automatically approved after this first warning)")
                    input()
                    first = False

                # file.rename(file.parent / str(new_name))  # tata.png
                shutil.copy(str(file), str(output_path / str(new_name)))

        print(f"Done. {len(files)} modified.")

        self.sanity_check(output_path, tmp_leng)

    @staticmethod
    def sanity_check(output_path: pathlib.Path, previous_files_length: int):
        print(f"Sanity check ... .")
        p_sanity = output_path.resolve().glob('**/*')
        files_sanity = [x for x in p_sanity if x.is_file()]
        tmp_leng_after_sanity = len(files_sanity)

        print(f"{previous_files_length} files before, {tmp_leng_after_sanity} after.")

        if previous_files_length != tmp_leng_after_sanity:
            raise Exception(f"Files lost ! {previous_files_length - tmp_leng_after_sanity} files deleted ? ")
        else:
            print(f"Same number of files before and after. All good.")

    def humanize_name(self, content: bytes, file_name: str, file_suffix: str, collision_removal: bool = True) -> str:  # toto.png

        # Python program to find SHA256 hexadecimal hash string of a file

        # new_name = codenamize(base64.b64encode(content), 3, 0) + file_suffix
        new_name = self.get_name(content, file_suffix)

        i = 0
        while collision_removal and self.is_already_drawn(new_name):  # tata.png
            print(f"Collision found on filename {file_name} generating {new_name}. Adding {i} to filename.")
            # Modify/Create a new name
            tmp_content = content + bytes(i)

            # Redraw the new name
            # new_name = codenamize(base64.b64encode(tmp_content), 3, 0) + file_suffix  # tata.png
            new_name = self.get_name(tmp_content, file_suffix)
            print(f"Collision handled by renaming {file_name} generating {new_name}.")
            i += 1

        # Correct the name for eventual
        final_name = self.correct_name(new_name)  # tata.png

        self.already_generated.add(final_name)  # tata.png

        return final_name  # tata.png

    @staticmethod
    def get_name(content, file_suffix: str) -> str:
        return codenamize(hashlib.sha256(content).hexdigest(), 3, 0) + file_suffix

    @staticmethod
    def correct_name(name: str) -> str:
        # Check for space in names, etc.
        final_name = name
        for l in [" ", "'"]:
            final_name = final_name.replace(l, '')

        if name != final_name:
            print(f"Name was corrected from {name} to {final_name}.")

        return final_name

    def is_already_drawn(self, new_name: str) -> bool:
        return {new_name}.issubset(self.already_generated)


def main():
    # Usage example : python3 ./humanizer.py -p ./MINI_DATASET/
    parser = argparse.ArgumentParser(description='Rename all files in the given directory and subdirectory')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), help='input path')
    parser.add_argument('-o', '--outpath', dest='outpath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='output path')
    parser.add_argument('--version', action='version', version='humanizer %s' % "1.0.0")

    args = parser.parse_args()
    humanizer = Humanizer()
    humanizer.rename_all_files(args.path, args.outpath)


def test():
    humanizer = Humanizer()
    print(humanizer.correct_name("toto is a test"))


if __name__ == "__main__":
    main()
