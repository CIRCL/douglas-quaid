#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import pathlib
import pprint


def save_json(obj, file_path: pathlib.Path):
    # TODO : To fix json_data = ast.literal_eval(json_data) ?
    #  See : https://stackoverflow.com/questions/25707558/json-valueerror-expecting-property-name-line-1-column-2-char-1

    # Create parents if they does not exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4)


def load_json(file_path: pathlib.Path):
    # !! : json.load() is for loading a file. json.loads() works with strings.
    # json.loads will load a json string into a python dict, json.dumps will dump a python dict to a json string,

    if file_path.is_file():
        # We have a valid file to load
        with open(str(file_path.resolve())) as json_file:
            data = json.load(json_file)
    else:
        raise Exception(f"Cannot load the provided path to json : path is not a valid file {file_path}")

    return data


class Dataturksparser:

    def __init__(self):
        self.to_export = None
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
