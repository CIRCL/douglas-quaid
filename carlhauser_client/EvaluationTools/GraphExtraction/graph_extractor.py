#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
from carlhauser_client.API.extended_api import Extended_API
import common.ImportExport.json_import_export as json_import_export

from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.edge import Edge
from common.Graph.node import Node

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class GraphExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ext_api = Extended_API.get_api()

    '''
    [ {'list_cluster': [{'cluster_id': 'cluster|d15fb88e-b6ad-4f74-b3f4-d631ea2c5a87',
                    'distance': 0.0},
                   {'cluster_id': 'cluster|143feb18-d930-4660-99c2-1da476c19a13',
                    'distance': 0.19285714285714287},
                   {'cluster_id': 'cluster|dc68c31f-6f9c-484e-a32b-8476a70a66fd',
                    'distance': 0.23035714285714284}],
      'list_pictures': [{'cluster_id': 'cluster|d15fb88e-b6ad-4f74-b3f4-d631ea2c5a87',
                         'distance': 0.0,
                         'image_id': 'advanzia3.png'},
                        {'cluster_id': 'cluster|d15fb88e-b6ad-4f74-b3f4-d631ea2c5a87',
                         'distance': 0.12109375,
                         'image_id': '90777ed4bdbd365059d9a2d86b01447be75c2103'},
                        {'cluster_id': 'cluster|d15fb88e-b6ad-4f74-b3f4-d631ea2c5a87',
                         'distance': 0.16428571428571428,
                         'image_id': 'advanzia1.png'},
                        {'cluster_id': 'cluster|d15fb88e-b6ad-4f74-b3f4-d631ea2c5a87',
                         'distance': 0.16607142857142856,
                         'image_id': 'advanzia2.png'},
                        {'cluster_id': 'cluster|d15fb88e-b6ad-4f74-b3f4-d631ea2c5a87',
                         'distance': 0.17232142857142857,
                         'image_id': 'a33756e54cfb61e93069c571bc7b09e44e556ee4'},
                        {'cluster_id': 'cluster|143feb18-d930-4660-99c2-1da476c19a13',
                         'distance': 0.19285714285714287,
                         'image_id': '824cacd1195fa5fa3f2555520dee23bfae3ee1f5'},
                        {'cluster_id': 'cluster|dc68c31f-6f9c-484e-a32b-8476a70a66fd',
                         'distance': 0.23035714285714284,
                         'image_id': '17cb810ceff1ead1f7ebaf348f61e7c2db84a676'}],
      'request_id': 'advanzia3.png',
      'request_time': 0.14145183563232422,
      'status': 'matches_found'},
    '''

    def construct_graph_from_results_list(self, requests_list, graph: GraphDataStruct, nb_match: int = 1) -> GraphDataStruct:
        # Construct a graph out of a full request list of results on the database
        # Hypothesis : All database pictures are requested pictures

        # Color Management for edges : from green to red depending on the match index
        # FF0000 = red
        # 00FF00 = green
        short_color_list = ["#00FF00", "#887700", "#CC3300", "#FF0000"]
        color_list = ["#00FF00", "#11EE00", "#22DD00", "#33CC00", "#44BB00", "#55AA00", "#669900", "#778800", "#887700", "#996600", "#AA5500", "#BB4400", "#CC3300", "#DD2200", "#EE1100", "#FF0000"]
        if nb_match < 4:
            color_list = short_color_list

        # For each request, add a node of the requested picture
        for curr_request in requests_list:
            graph.add_node(Node(label=curr_request["request_id"], id=curr_request["request_id"], image=curr_request["request_id"]))

        # For each request, add the edge between the request picture and his match, if not itself
        for curr_request in requests_list:

            # We remove the picture "itself" from the matches
            tmp_clean_matches = []
            for match in curr_request.get("list_pictures", []):
                if match["image_id"] != curr_request["request_id"]:
                    tmp_clean_matches.append(match)
                elif match["distance"] != 0:
                    self.logger.warning(f"Picture {curr_request['request_id']} has not a distance 0 to itself. Strange.")

            '''
             # Perform sanity check about "the best match is itself"
            offset = 0
            if len(curr_request["list_pictures"]) >= 1 and curr_request["list_pictures"][0]["image_id"] == curr_request["request_id"]:
                # Best match is itself, add an offset to all next matches
                offset += 1
            else:
                self.logger.warning(f"Picture {curr_request['request_id']} best match is not itself. Strange. Better to investigate.")

            '''

            # Add best pictures
            for i in range(min(nb_match, len(tmp_clean_matches))):
                graph.add_edge(Edge(_from=curr_request["request_id"],
                                    _to=tmp_clean_matches[i]["image_id"],
                                    color={"color": color_list[i % len(color_list)]},
                                    label=str(tmp_clean_matches[i]["distance"]),
                                    value=tmp_clean_matches[i]["distance"]))

        return graph

    def launch(self, image_folder: pathlib.Path, output_path: pathlib.Path, visjs_json_path: pathlib.Path = None):
        # Compute a complete run of the library on a folder, to extract the graph of proximity from/for each picture
        # Not as efficient as it could be, as it is not the normal way of work of the library

        # ========= MANUAL EVALUATION =========

        if visjs_json_path is None:
            self.logger.warning(f"VisJS ground truth path not set. Impossible to evaluate.")
        else:
            self.logger.info(f"VisJS ground truth path set. Graph will be evaluated.")
            # 1. Load pictures to visjs = node server.js -i ./../douglas-quaid/datasets/MINI_DATASET/ -t ./TMP -o ./TMP
            # 2. Cluster manually pictures in visjs = < Do manual stuff>
            # 3. Load json graphe
            visjs = json_import_export.load_json(visjs_json_path)
            visjs = GraphDataStruct.load_from_dict(visjs)


        # ========= AUTO EVALUATION =========
        # Send pictures to DB and get id mapping
        mapping_old_filename_to_new_id, nb_pictures = self.ext_api.add_pictures_to_db(image_folder)
        time.sleep(10)  # Let time to add pictures to db

        # Get a DB dump
        requests_result, nb_pictures = self.ext_api.request_pictures(image_folder)

        revert_mapping = self.ext_api.revert_mapping(mapping_old_filename_to_new_id)
        # graphe_struct.replace_id_from_mapping(mapping) #TODO : do it with graphes ?
        requests_result = self.ext_api.apply_revert_mapping(requests_result, revert_mapping)

        # pprint.pprint(requests_result)
        save_path_json = output_path / "requests_result.json"
        json_import_export.save_json(requests_result, save_path_json)
        self.logger.debug(f"Request results json saved in : {save_path_json}")

        # ========= Graph building =========

        tmp_graph = GraphDataStruct(meta=Metadata(source=Source.DBDUMP))
        tmp_graph = self.construct_graph_from_results_list(requests_result, tmp_graph, nb_match=2)
        # pprint.pprint(tmp_graph.export_as_dict())

        save_path_json = output_path / "distance_graph.json"
        json_import_export.save_json(tmp_graph.export_as_dict(), save_path_json)
        self.logger.debug(f"Distance graph json saved in : {save_path_json}")

        if visjs_json_path is not None:
            # ========= Graph evaluation =========
            '''
            perf_eval = GraphQualityEvaluator()
            perfs = perf_eval.evaluate_performance(tmp_graph, visjs)  # graph ==> Quality score for each

            save_path_json = output_path / "graph_perfs.json"
            json_import_export.save_json(perfs, save_path_json)
            self.logger.debug(fGraph performances json saved in : {save_path_json}")
            
            '''

        '''
        # ========= CONSTRUCT GRAPHE =========
        # Apply name mapping to dict (find back original names)
        visjs.replace_id_from_mapping(mapping_old_filename_to_new_id)

        # Get only list of clusters
        candidate = db_dump.get_clusters()
        original = visjs.get_clusters()

        # Match clusters
        # 1. Manually ? (Go back to visjs + rename)
        # 2. Automatically ? (Number of common elements ~)
        matcher = Cluster_matcher()
        matching = matcher.match_clusters(original, candidate)  # Matching original + Candidate ==> Group them per pair

        # Compute performance regarding input graphe
        perf_eval = ClusterMatchingQualityEvaluator()
        matching_with_perf = perf_eval.evaluate_performance(matching, nb_pictures)  # pair of clusters ==> Quality score for each

        # Store performance in a file
        save_path_perf = output_path / "perf.json"
        perf_overview = perf_eval.save_perf_results(save_path_perf)

        # ========= RESULT VISUALIZATON =========

        # Convert matching with performance to confusion matrix
        matrix_creator = ConfusionMatrixGenerator()
        matrix_creator.create_and_export_confusion_matrix(original, candidate, matching, output_path / "matrix.pdf")  # Matching original + Candidate ==> Group them per pair

        # Convert dumped graph to visjs graphe
        # ==> red if linked made by algo, but non existant + Gray, true link that should have been created (
        # ==> Green if linked made by algo and existant
        save_path_json = output_path / "merged_graph.json"
        output_graph = merge_graphs(visjs, db_dump, matching)
        json_import_export.save_json(output_graph, save_path_json)
        self.logger.debug(f"DB Dump json saved in : {save_path_json}")

        # ==============================

        return perf_overview
        '''


'''
def main():
    parser = argparse.ArgumentParser(description='Perform an evaluation on a dataset : Send all pictures, ')
    parser.add_argument('-p', '--path', dest='path', action='store', type=lambda p: pathlib.Path(p).absolute(), default=1, help='all path')
    parser.add_argument('--version', action='version', version='humanizer %s' % ("1.0.0"))

    args = parser.parse_args()
    humanizer = Humanizer()
    humanizer.rename_all_files(args.path)

'''


def test():
    evaluator = GraphExtractor()
    image_folder = get_homedir() / "datasets" / "MINI_DATASET"
    # image_folder = get_homedir() / "datasets" / "raw_phishing_full"
    output_path = get_homedir() / "carlhauser_client"
    evaluator.launch(image_folder, output_path)


if __name__ == "__main__":
    test()
