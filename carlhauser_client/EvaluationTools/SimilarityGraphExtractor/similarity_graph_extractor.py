#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import pathlib

import common.ImportExport.json_import_export as json_import_export
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_client.Helpers.dict_utilities import get_clear_matches
from common.Graph.edge import Edge
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.node import Node
from common.environment_variable import get_homedir
from common.environment_variable import load_client_logging_conf_file

load_client_logging_conf_file()


# ==================== ------ LAUNCHER ------- ====================
class GraphExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ext_api: Extended_API = Extended_API.get_api()

    # ======================== EXTRACT GRAPH FROM DB  ========================

    def get_proximity_graph(self, image_folder: pathlib.Path, output_path: pathlib.Path) -> GraphDataStruct:
        '''
        Extract a proximity graph from a folder of pictures, sent to DB and requested one by one.
        :param image_folder: The folder of picture to send and request, to build the similarity graph from
        :param output_path: The output path where the graph and other data will be stored
        :return: the proximity graph
        '''

        # Get distance results for each picture
        list_results = self.ext_api.add_and_request_and_dump_pictures(image_folder)

        # Save to file
        json_import_export.save_json(list_results, output_path / "requests_result.json")
        self.logger.debug(f"Results raw json saved.")

        # Construct graph from the list of distance results
        tmp_graph = self.results_list_to_graph(list_results, nb_match=2)

        # Save to file
        json_import_export.save_json(tmp_graph.export_as_dict(), output_path / "distance_graph.json")
        self.logger.debug(f"Distance graph json saved.")

        return tmp_graph

    @staticmethod
    def results_list_to_graph(requests_list, nb_match: int = 1) -> GraphDataStruct:
        '''
        Construct a graph from results list of requests on the database
        Hypothesis : All database pictures are requested pictures
        Edges are colored : from green to red depending on the match index (Best is green)
        :param requests_list: a List of results extracted from server
        :param nb_match: Number of matches per pictures to add to the graph (1=first level match/best match, 2 = 2 best match per picture, etc.)
        :return: A graph datastructure
        '''

        graph = GraphDataStruct(meta=Metadata(source=Source.DBDUMP))

        # Color Managemement
        # FF0000 = red
        # 00FF00 = green
        short_color_list = ["#00FF00", "#887700", "#CC3300", "#FF0000"]
        color_list = ["#00FF00", "#11EE00", "#22DD00", "#33CC00", "#44BB00", "#55AA00",
                      "#669900", "#778800", "#887700", "#996600", "#AA5500", "#BB4400",
                      "#CC3300", "#DD2200", "#EE1100", "#FF0000"]

        if nb_match < 4:
            # We only have 4 colors if we don't want that much matches.
            # This way, first match is green, second orange, third red, etc.
            color_list = short_color_list

        # For each request
        for curr_request in requests_list:
            # Requested picture => add a node
            graph.add_node(Node(label=curr_request["request_id"], id=curr_request["request_id"], image=curr_request["request_id"]))

        # For each request
        for curr_request in requests_list:

            # We remove the picture "itself" from the matches
            tmp_clean_matches = get_clear_matches(curr_request)

            # Add edge for each best pictures
            for i in range(min(nb_match, len(tmp_clean_matches))):
                graph.add_edge(Edge(_from=curr_request["request_id"],
                                    _to=tmp_clean_matches[i]["image_id"],
                                    color={"color": color_list[i % len(color_list)]},
                                    label=str(tmp_clean_matches[i]["distance"]),
                                    value=tmp_clean_matches[i]["distance"]))

        return graph


''' Example of result
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


def test():
    evaluator = GraphExtractor()
    image_folder = get_homedir() / "datasets" / "MINI_DATASET"
    # image_folder = get_homedir() / "datasets" / "raw_phishing_full"
    output_path = get_homedir() / "carlhauser_client"
    evaluator.get_proximity_graph(image_folder, output_path)


if __name__ == "__main__":
    test()
