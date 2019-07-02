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


class VisJSsparser:

    def __init__(self):
        self.to_export = None

        self.num_to_name_dict = {}
        self.file_names_to_delete = set({})

    def load_file(self, inputfile_path: pathlib.Path):
        tmp_json = load_json(inputfile_path)
        pprint.pprint(tmp_json)

        self.to_export = []
        self.num_to_name_dict = {}

        '''
          "nodes": [
            {
              "id": 0,
              "image": "abashed-careless-ordinary-crew.png",
              "shape": "image"
            },
            {
              "id": 1,
              "image": "ablaze-jazzy-tangy-file.png",
              "shape": "image"
            },
        '''

        # Construct dict id -> name
        for picture in tmp_json["nodes"]:
            self.num_to_name_dict[picture.get("id")] = picture.get("image")


        tmp_cluster_list = []

        # Modify clusters
        for cluster in tmp_json["clusters"]:
            tmp_cluster = {}

            tmp_cluster["cluster"] = cluster.get("label")
            tmp_cluster_list.append(cluster.get("label"))

            # Add tranlated member name
            tmp_members = []
            for members in cluster.get("members") :
                tmp_members.append(self.num_to_name_dict[members])

            tmp_cluster["members"] = tmp_members

            self.to_export.append(tmp_cluster)

        print(tmp_cluster_list)


    def export_file(self, outputfile_path: pathlib.Path):

        if self.to_export is not None :
            save_json(self.to_export, outputfile_path)
            print(f"File exported to : {outputfile_path} with {len(self.to_export)} entries.")


def main():
    # Usage example : python3 ./dataturks_parser.py -p ./dataturks.json -o ./dataturksjson_cleaned.json
    parser = argparse.ArgumentParser(description='Parse visjs json, extract list of picture to delete, delete them, and save a "clean version" of the json.')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), help='input json path (to file)')
    parser.add_argument('-o', '--outpath', dest='outpath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='output json path (to folder)')
    parser.add_argument('--version', action='version', version='humanizer %s' % "1.0.0")

    args = parser.parse_args()
    parser = VisJSsparser()

    parser.load_file(args.path)
    parser.export_file(args.outpath)

if __name__ == "__main__":
    main()

