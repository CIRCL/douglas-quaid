#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
import pprint
from typing import List, Dict

import matplotlib.pyplot as plt
import numpy as np

from common.ImportExport.json_import_export import load_json


class DataturksGraph:

    def __init__(self):
        self.to_export = []
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
        labels_sets = {}

        # For each picture
        for picture in tmp_json:
            tmp_final_object = {}
            tmp_final_object["picture"] = picture.get("content")  # 'fat-noxious-doubtful-walk.png'
            tmp_annotation = picture.get("annotation")

            # If there is annotation for this picture
            if tmp_annotation is not None:
                # Store the number of annotation of this kind
                extracted_clusters = [self.strip_tag(label) for label in tmp_annotation.get('labels')]

                # Store each cluster frequency
                for cluster in extracted_clusters:  # ['Steam']
                    clusters[cluster] = clusters.get(cluster, 0) + 1

                # Store each set of clusters frequency
                tmp_set, tmp_key = self.create_set_from_labels_list(extracted_clusters)
                # We store only pairs, at least
                if len(tmp_set) > 1:
                    labels_sets[tmp_key] = labels_sets.get(tmp_key, 0) + 1

            else:
                print(f"Annotation void for picture : {tmp_final_object['picture']}")

        # Print the labels names frequencies
        list_key, list_val = self.get_list_val_list_key_from_dict(clusters)
        self.draw_plot(list_key, list_val, outputfile_path / "fig_simple.pdf")

        # Remove too low sets :
        frequent_only = {k: v for k, v in labels_sets.items() if v > 10}
        # Print the set of labels names frequencies
        list_key, list_val = self.get_list_val_list_key_from_dict(frequent_only)
        self.draw_plot(list_key, list_val, outputfile_path / "fig_set.pdf", log_scale=True)

    @staticmethod
    def get_list_val_list_key_from_dict(mydict: Dict):
        # Return a list of keys and a list of values from a dict.
        list_key = []
        list_val = []
        for key, value in sorted(mydict.items(), key=lambda item: item[1]):
            list_key.append(key)
            list_val.append(value)
        return list_key, list_val

    @staticmethod
    def create_set_from_labels_list(labels: List[str]):
        # Create a set of labels from a list of labels and an identifier key
        labels.sort()

        # Create the key
        key = ' + '.join(labels)

        # Create the set
        s = set()
        for l in labels:
            s.add(l)
        return s, key

    @staticmethod
    def strip_tag(tag: str):
        # test = 'dark - web: structure = "legal-statement"'
        # to_delete
        index = tag.find('"')
        if index != -1:
            return tag[tag.find('"') + 1:-1]
        else:
            return tag

    @staticmethod
    def draw_plot(labels, value, save_path: pathlib.Path, log_scale=False):
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
        if log_scale:
            ax.set_xscale('log')
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Nb items')
        ax.set_title('How many items per cluster')

        plt.savefig(save_path)
        plt.show()


def main():
    # Usage example : XXX
    # python3 ./dataturks_graph.py  -p ./../../../totalrecall/Dataturks_phishing_classification.json -o ./
    parser = argparse.ArgumentParser(description='Parse dataturks json, save a frequency graph of labels.')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), help='input json path (to file)')
    parser.add_argument('-f', '--filespath', dest='filespath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='files path (to folder)')
    parser.add_argument('-o', '--outpath', dest='outpath', action='store', type=lambda p: pathlib.Path(p).absolute(), help='output json path (to folder)')
    parser.add_argument('--version', action='version', version='humanizer %s' % "1.0.0")

    args = parser.parse_args()
    parser = DataturksGraph()

    parser.load_file(args.path, args.outpath)


if __name__ == "__main__":
    main()
