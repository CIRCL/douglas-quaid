#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time
from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir
from carlhauser_client.API.extended_api import Extended_API
import carlhauser_client.EvaluationTools.GraphExtraction.graph_quality_evaluator as graph_quality_evaluator
import common.ImportExport.json_import_export as json_import_export

from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.edge import Edge
from common.Graph.node import Node
import common.PerformanceDatastructs.perf_datastruct as perf_datastruct

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
                         'image_id': 'advanzia3.png'}, (...)
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

    def load_visjs_to_graphe(self, visjs_json_path: pathlib.Path = None) -> GraphDataStruct:

        if visjs_json_path is None:
            self.logger.warning(f"VisJS ground truth path not set. Impossible to evaluate.")
            return None
        else:
            self.logger.info(f"VisJS ground truth path set. Graph will be evaluated.")
            # 1. Load pictures to visjs = node server.js -i ./../douglas-quaid/datasets/MINI_DATASET/ -t ./TMP -o ./TMP
            # 2. Cluster manually pictures in visjs = < Do manual stuff>
            # 3. Load json graphe
            visjs = json_import_export.load_json(visjs_json_path)
            visjs = GraphDataStruct.load_from_dict(visjs)

            return visjs

    def send_pictures_and_dump(self, image_folder: pathlib.Path):

        # Send pictures to DB and get id mapping
        mapping_old_filename_to_new_id, nb_pictures = self.ext_api.add_pictures_to_db(image_folder)
        time.sleep(10)  # Let time to add pictures to db

        # Get a DB dump
        requests_result, nb_pictures = self.ext_api.request_pictures(image_folder)

        revert_mapping = self.ext_api.revert_mapping(mapping_old_filename_to_new_id)
        # graphe_struct.replace_id_from_mapping(mapping) #TODO : do it with graphes ?
        requests_result = self.ext_api.apply_revert_mapping(requests_result, revert_mapping)

        return requests_result

    def save_result_to_file(self, requests_result, output_file_path: pathlib.Path):
        # pprint.pprint(requests_result)
        json_import_export.save_json(requests_result, output_file_path)
        self.logger.debug(f"Json saved in : {output_file_path}")

    def construct_graph_from_results(self, requests_result) -> GraphDataStruct:
        tmp_graph = GraphDataStruct(meta=Metadata(source=Source.DBDUMP))
        tmp_graph = self.construct_graph_from_results_list(requests_result, tmp_graph, nb_match=2)
        # pprint.pprint(tmp_graph.export_as_dict())
        return tmp_graph

    def launch(self, image_folder: pathlib.Path,
               output_path: pathlib.Path,
               visjs_json_path: pathlib.Path = None) -> List[perf_datastruct.Perf]:
        # Compute a complete run of the library on a folder, to extract the graph of proximity from/for each picture
        # Not as efficient as it could be, as it is not the normal way of work of the library

        # ========= MANUAL EVALUATION =========
        visjs = self.load_visjs_to_graphe(visjs_json_path)

        # ========= AUTO EVALUATION =========
        requests_result = self.send_pictures_and_dump(image_folder)

        # Save to file
        self.save_result_to_file(requests_result, output_path / "requests_result.json")
        self.logger.debug(f"Results raw json saved.")

        # ========= GRAPH BUILDING =========
        tmp_graph = self.construct_graph_from_results(requests_result)

        # Save to file
        self.save_result_to_file(tmp_graph.export_as_dict(), output_path / "distance_graph.json")
        self.logger.debug(f"Distance graph json saved.")

        # ========= GRAPH QUALITY EVALUATION =========
        if visjs_json_path is not None:
            perf_eval = graph_quality_evaluator.GraphQualityEvaluator()
            perfs = perf_eval.evaluate_performance(tmp_graph, visjs)  # graph ==> Quality score for each

            # Save to file
            self.save_result_to_file(perfs, output_path / "graph_perfs.json")
            self.logger.debug(f"Graph performances json saved.")
            return perfs


def test():
    evaluator = GraphExtractor()
    image_folder = get_homedir() / "datasets" / "MINI_DATASET"
    # image_folder = get_homedir() / "datasets" / "raw_phishing_full"
    output_path = get_homedir() / "carlhauser_client"
    evaluator.launch(image_folder, output_path)


if __name__ == "__main__":
    test()
