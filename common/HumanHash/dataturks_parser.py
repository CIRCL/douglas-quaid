#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
import pprint

from common.ImportExport.json_import_export import save_json, load_json


class Dataturksparser:

    def __init__(self):
        self.to_export = []
        self.file_names_to_delete = set({})

    def load_file(self, inputfile_path: pathlib.Path):
        tmp_json = load_json(inputfile_path)
        pprint.pprint(tmp_json)

        self.to_export = []

        '''
                       (...),
         {'annotation': 
            {
                'labels': ['Steam'], 
                'note': ''
            },
          'content': 'fat-noxious-doubtful-walk.png',
          'metadata': {'evaluation': 'NONE',
                       'first_done_at': 1561366939000,
                       'last_updated_at': 1561366939000,
                       'last_updated_by': 'user',
                       'sec_taken': 0,
                       'status': 'done'}}]
        '''

        for picture in tmp_json:
            tmp_final_object = {}
            tmp_final_object["picture"] = picture.get("content")  # 'fat-noxious-doubtful-walk.png'
            tmp_annotation = picture.get("annotation")
            if tmp_annotation is not None:
                tmp_final_object["labels"] = tmp_annotation.get('labels')  # ['Steam']

                if "to_delete" in tmp_final_object["labels"]:
                    # mark to be deleted
                    self.file_names_to_delete.add(tmp_final_object["picture"])
                    print(f"{tmp_final_object['picture']} mark to be deleted.")

                else:
                    # Add to export
                    self.to_export.append(tmp_final_object)
                    # print(f"{tmp_final_object} mark to be exported.")

            else:
                print(f"Annotation void for picture : {tmp_final_object['picture']}")

    def delete_marked_files(self, folder_path: pathlib.Path):

        if len(self.file_names_to_delete) != 0:
            p = folder_path.resolve().glob('**/*')
            files = [x for x in p if x.is_file()]

            # For each file found, if present in to_delete list, delete it
            for file in files:
                if file.name in self.file_names_to_delete:
                    file.unlink()
                    print(f"File {file.name} deleted.")

    def export_file(self, outputfile_path: pathlib.Path):

        if self.to_export is not None:
            save_json(self.to_export, outputfile_path)
            print(f"File exported to : {outputfile_path} with {len(self.to_export)} entries.")


def main():
    # Usage example : python3 ./dataturks_parser.py -p ./dataturks.json -f ./MINI_DATASET -o ./dataturksjson_cleaned.json
    # python3 ./dataturks_parser.py  -p ./../../../totalrecall/Dataturks_phishing_classification.json -f ./../../../DATASETS/output_try_to_clean/ -o ./dataturks_clean.json
    parser = argparse.ArgumentParser(description='Parse dataturks json, extract list of picture to delete, delete them, and save a "clean version" of the json.')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), help='input json path (to file)')
    parser.add_argument('-f', '--filespath', dest='filespath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='files path (to folder)')
    parser.add_argument('-o', '--outpath', dest='outpath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='output json path (to folder)')
    parser.add_argument('--version', action='version', version='humanizer %s' % "1.0.0")

    args = parser.parse_args()
    parser = Dataturksparser()

    parser.load_file(args.path)
    parser.delete_marked_files(args.filespath)
    parser.export_file(args.outpath)


if __name__ == "__main__":
    main()
