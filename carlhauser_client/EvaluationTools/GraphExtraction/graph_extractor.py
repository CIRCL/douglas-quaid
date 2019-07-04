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
import common.PerformanceDatastructs.thresholds_datastruct as thresholds_datastruct
from common.ChartMaker.two_dimensions_plot import TwoDimensionsPlot


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
            self.logger.warning("VisJS ground truth path not set. Impossible to evaluate.")
            raise Exception("VisJS ground truth path not set. Impossible to evaluate.")
        else:
            self.logger.info("VisJS ground truth path set. Graph will be evaluated.")
            # 1. Load pictures to visjs = node server.js -i ./../douglas-quaid/datasets/MINI_DATASET/ -t ./TMP -o ./TMP
            # 2. Cluster manually pictures in visjs = < Do manual stuff>
            # 3. Load json graphe
            visjs = json_import_export.load_json(visjs_json_path)
            visjs = GraphDataStruct.load_from_dict(visjs)

            return visjs

    # ======================== GET RESULTS FROM FOLDER OF PICTURES ========================

    def send_pictures_and_dump_and_save(self, image_folder: pathlib.Path, output_path: pathlib.Path) -> List:
        requests_result = self.send_pictures_and_dump(image_folder)

        # Save to file
        json_import_export.save_json(requests_result, output_path / "requests_result.json")
        self.logger.debug(f"Results raw json saved.")
        return requests_result

    def send_pictures_and_dump(self, image_folder: pathlib.Path) -> List:
        # Send pictures of a folder to DB and request all pictures one by one, to construct a list of results

        # Send pictures to DB and get id mapping
        mapping_old_filename_to_new_id, nb_pictures = self.ext_api.add_pictures_to_db(image_folder)
        time.sleep(10)  # Let time to add pictures to db

        # Get a DB dump
        requests_result, nb_pictures = self.ext_api.request_pictures(image_folder)

        revert_mapping = self.ext_api.revert_mapping(mapping_old_filename_to_new_id)
        # graphe_struct.replace_id_from_mapping(mapping) #TODO : do it with graphes ?
        requests_result = self.ext_api.apply_revert_mapping(requests_result, revert_mapping)

        return requests_result

    # ======================== GRAPH FROM RESULTS ========================
    def construct_graph_from_results_and_save(self, requests_result, output_path: pathlib.Path) -> GraphDataStruct:
        tmp_graph = self.construct_graph_from_results(requests_result)
        # Save to file
        json_import_export.save_json(tmp_graph.export_as_dict(), output_path / "distance_graph.json")
        self.logger.debug(f"Distance graph json saved.")
        return tmp_graph

    def construct_graph_from_results(self, requests_result) -> GraphDataStruct:
        tmp_graph = GraphDataStruct(meta=Metadata(source=Source.DBDUMP))
        tmp_graph = self.construct_graph_from_results_list(requests_result, tmp_graph, nb_match=2)
        # pprint.pprint(tmp_graph.export_as_dict())
        return tmp_graph

    # ======================== High-Level functions : Extract data/graph from DB ========================

    def get_distance_graph_from_db(self, image_folder: pathlib.Path, output_path: pathlib.Path) -> GraphDataStruct:
        # Extract a distance graph from a folder of pictures, sent to DB and requested one by one.

        # Get distance results for each picture
        requests_result = self.send_pictures_and_dump_and_save(image_folder, output_path)

        # Construct graph for the list of distance results
        tmp_graph = self.construct_graph_from_results_and_save(requests_result, output_path)

        return tmp_graph

    def get_best_algorithm_threshold(self, image_folder: pathlib.Path,
                                     output_path: pathlib.Path,
                                     visjs_json_path: pathlib.Path) -> (List[perf_datastruct.Perf], thresholds_datastruct.Thresholds):
        # Compute the best threshold to apply to distance, from the current state of the library
        self.logger.debug(f"Finding best thresholds ... ")

        # Get results from DB and ground truth graph from visjs file
        requests_result = self.send_pictures_and_dump_and_save(image_folder, output_path)
        gt_graph = self.load_visjs_to_graphe(visjs_json_path)
        perf_eval = graph_quality_evaluator.GraphQualityEvaluator()

        # Call the graph evaluator on this pair result_list + gt_graph
        perfs_list = perf_eval.get_perf_list(requests_result, gt_graph)  # ==> List of scores

        # Save to file
        json_import_export.save_json(perfs_list, output_path / "graph_perfs.json")
        self.logger.debug(f"Graph performances json saved.")

        # Save to graph
        twoDplot = TwoDimensionsPlot()
        twoDplot.print_graph(perfs_list, output_path)

        # Call the graph evaluator on this pair result_list + gt_graph
        mTP = perf_eval.get_max_TP(perfs_list)  # ==> List of scores
        mTN = perf_eval.get_min_FP(perfs_list)  # ==> List of scores
        mM = perf_eval.get_mean(perfs_list)  # ==> List of scores

        thresholds_holder = thresholds_datastruct.Thresholds(max_TPR=mTP, max_FPR=mTN, mean=mM)
        self.logger.debug(f"Computed thresholds {thresholds_holder} ")

        # Save to graph
        twoDplot.print_graph_with_thresholds(perfs_list, thresholds_holder, output_path)

        return perfs_list, thresholds_holder


def test():
    evaluator = GraphExtractor()
    image_folder = get_homedir() / "datasets" / "MINI_DATASET"
    # image_folder = get_homedir() / "datasets" / "raw_phishing_full"
    output_path = get_homedir() / "carlhauser_client"
    evaluator.get_distance_graph_from_db(image_folder, output_path)


if __name__ == "__main__":
    test()
