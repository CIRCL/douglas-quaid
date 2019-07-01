#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
import pprint
import hashlib
import shutil
from typing import Set
import json
import matplotlib.pyplot as plt
import numpy as np
import collections


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


class DataturksGraph():

    def __init__(self):
        self.to_export = None
        self.file_names_to_delete = set({})

    def load_file(self, inputfile_path: pathlib.Path, outputfile_path: pathlib.Path):
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

        clusters = {}

        for picture in tmp_json:
            tmp_final_object = {}
            tmp_final_object["picture"] = picture.get("content")  # 'fat-noxious-doubtful-walk.png'
            tmp_annotation = picture.get("annotation")
            if tmp_annotation is not None:
                for cluster in tmp_annotation.get('labels'):  # ['Steam']
                    clusters[cluster] = clusters.get(cluster, 0) + 1
            else:
                print(f"Annotation void for picture : {tmp_final_object['picture']}")

        list_key = []
        list_val = []
        for key, value in sorted(clusters.items(), key=lambda item: item[1]):
            list_key.append(key)
            list_val.append(value)

        self.draw_plot(list_key, list_val, outputfile_path / "fig.pdf")

    def draw_plot(self, labels, value, save_path: pathlib.Path):
        # Fixing random state for reproducibility
        np.random.seed(19680801)

        plt.rcdefaults()
        fig, ax = plt.subplots()

        # Example data
        # people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')
        y_pos = np.arange(len(labels))
        # performance = 3 + 10 * np.random.rand(len(people))
        # error = np.random.rand(len(people))

        ax.barh(y_pos, value, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Nb items')
        ax.set_title('How many items per cluster')

        plt.savefig(save_path)
        plt.show()


def main():
    # Usage example : XXX
    # python3 ./dataturks_graph.py  -p ./../../../totalrecall/Dataturks_phishing_classification.json -o ./
    parser = argparse.ArgumentParser(description='Parse dataturks json, extract list of picture to delete, delete them, and save a "clean version" of the json.')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), help='input json path (to file)')
    parser.add_argument('-f', '--filespath', dest='filespath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='files path (to folder)')
    parser.add_argument('-o', '--outpath', dest='outpath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='output json path (to folder)')
    parser.add_argument('--version', action='version', version='humanizer %s' % ("1.0.0"))

    args = parser.parse_args()
    parser = DataturksGraph()

    parser.load_file(args.path, args.outpath)


if __name__ == "__main__":
    main()
