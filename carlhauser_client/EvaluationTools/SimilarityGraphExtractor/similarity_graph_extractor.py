#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging.config
import pathlib
from pprint import pformat
from typing import List, Dict

import common.ImportExport.json_import_export as json_import_export
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_client.Helpers.dict_utilities import get_clear_matches
from common.Graph.edge import Edge
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.node import Node
from common.environment_variable import get_homedir
from common.environment_variable import load_client_logging_conf_file
from common.environment_variable import dir_path
import carlhauser_client.EvaluationTools.SimilarityGraphExtractor.similarity_graph_quality_evaluator as similarity_graph_quality_evaluator
import common.Graph.graph_datastructure as graph_datastructure
import common.Calibrator.calibrator_conf as calibrator_conf
import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
import common.ChartMaker.two_dimensions_plot as two_dimensions_plot
import carlhauser_server.DistanceEngine.scoring_datastrutures as scoring_datastrutures

load_client_logging_conf_file()


# ==================== ------ LAUNCHER ------- ====================
class GraphExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ext_api: Extended_API = Extended_API.get_api()

    # ======================== EXTRACT GRAPH FROM DB  ========================

    def get_proximity_graph_and_evaluate(self, image_folder: pathlib.Path, output_path: pathlib.Path, gt_path: pathlib.Path):
        list_results, _ = self.get_proximity_graph(image_folder, output_path)
        perfs_list = self.evaluate_list_results(list_results, gt_path, output_path)

        # Save to file
        json_import_export.save_json(perfs_list, output_path / "perfs_list.json")
        self.logger.debug(f"Performance list saved.")

        # Save to graph
        twoDplot = two_dimensions_plot.TwoDimensionsPlot()
        twoDplot.print_graph(perfs_list, output_path)

    def evaluate_list_results(self, list_results: List[Dict],
                              gt_path: pathlib.Path,
                              output_path: pathlib.Path,
                              cal_conf: calibrator_conf.Default_calibrator_conf = calibrator_conf.Default_calibrator_conf()) -> List[perf_datastruct.Perf]:

        # Load ground truth file
        gt_graph = graph_datastructure.load_visjs_to_graph(gt_path)

        # tmp_cal_conf = calibrator_conf.Default_calibrator_conf()

        # Call the graph evaluator on this pair result_list + gt_graph
        self.logger.debug(f"Extracting performance list ")
        perf_eval = similarity_graph_quality_evaluator.similarity_graph_quality_evaluator(cal_conf)
        perfs_list = perf_eval.get_perf_list(list_results, gt_graph)  # ==> List of scores
        self.logger.debug(f"Fetched performance list : {pformat(perfs_list)} ")

        # Do same for decisions
        perf_eval.get_perf_list_decision(list_results, gt_graph, output_folder=output_path)

        return perfs_list

    def get_proximity_graph(self, image_folder: pathlib.Path, output_path: pathlib.Path) -> (List[Dict], GraphDataStruct):
        """
        Extract a proximity graph from a folder of pictures, sent to DB and requested one by one.
        :param image_folder: The folder of picture to send and request, to build the similarity graph from
        :param output_path: The output path where the graph and other data will be stored
        :return: the proximity graph
        """

        # Get distance results for each picture
        # list_results = self.ext_api.add_and_request_and_dump_pictures(image_folder)

        # Save to file
        # json_import_export.save_json(list_results, output_path / "requests_result.json")
        # DEBUG IF FAILURE FOR MANUAL RECOVERY #
        list_results = json_import_export.load_json(output_path / "requests_result.json")
        self.logger.debug(f"Results raw json saved.")

        #  DEBUG IF FAILURE FOR MANUAL RECOVERY #
        list_results = [r for r in list_results if r is not None and r.get("request_id", None) is not None]

        # Extract tmp_graph and save as graphs
        tmp_graph = self.get_proximity_graph_from_list_result(list_results, output_path)

        '''
        # Construct graph from the list of distance results
        tmp_graph = self.results_list_to_graph(list_results, nb_match=2)

        # Save to file
        json_import_export.save_json(tmp_graph.export_as_dict(), output_path / "distance_graph.json")
        self.logger.debug(f"Distance graph json saved.")

        # Construct graph from the list of distance results
        tmp_graph = self.results_list_to_graph(list_results, nb_match=2, yes_maybe_no_mode=True)

        # Save to file
        json_import_export.save_json(tmp_graph.export_as_dict(), output_path / "distance_graph_yes_maybe_no.json")
        self.logger.debug(f"Distance graph yes-maybe-no json saved.")
        '''
        return list_results, tmp_graph


    def get_proximity_graph_from_list_result(self, list_results : List[Dict], output_path : pathlib.Path) -> GraphDataStruct:

        # Construct graph from the list of distance results
        tmp_graph = self.results_list_to_graph(list_results, nb_match=2)

        # Save to file
        json_import_export.save_json(tmp_graph.export_as_dict(), output_path / "distance_graph.json")
        self.logger.debug(f"Distance graph json saved.")

        # Construct graph from the list of distance results
        tmp_graph = self.results_list_to_graph(list_results, nb_match=2, yes_maybe_no_mode=True)

        # Save to file
        json_import_export.save_json(tmp_graph.export_as_dict(), output_path / "distance_graph_yes_maybe_no.json")
        self.logger.debug(f"Distance graph yes-maybe-no json saved.")

        return tmp_graph

    @staticmethod
    def results_list_to_graph(requests_list, nb_match: int = 1, yes_maybe_no_mode: bool = False) -> GraphDataStruct:
        """
        Construct a graph from results list of requests on the database
        Hypothesis : All database pictures are requested pictures
        Edges are colored : from green to red depending on the match index (Best is green)
        :param requests_list: a List of results extracted from server
        :param nb_match: Number of matches per pictures to add to the graph (1=first level match/best match, 2 = 2 best match per picture, etc.)
        :return: A graph datastructure
        """
        logger = logging.getLogger(__name__)
        # logger.debug(f"Received request_list : {pformat(requests_list)}")

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
        # TODO : Print all YES match

        # For each request
        for curr_req_1 in requests_list:
            # logger.debug(f"Curent request : {pformat(curr_req_1)}")
            req_id = curr_req_1.get("request_id", None)

            # Requested picture => add a node
            graph.add_node(Node(label=req_id, id=req_id, image=req_id))

        # For each request
        for curr_req_2 in requests_list:

            # We remove the picture "itself" from the matches
            tmp_clean_matches = get_clear_matches(curr_req_2)

            req_id = curr_req_2.get("request_id", None)

            # Add edge for each best pictures
            for i in range(min(nb_match, len(tmp_clean_matches))):

                dist = round(tmp_clean_matches[i].get("distance", None), 4)
                deci = tmp_clean_matches[i].get("decision", "UNKNOWN")
                dest_id = tmp_clean_matches[i].get("image_id", None)

                if dist is None:
                    logger.error(f"Problem with request, no distance: {pformat(curr_req_2)}")
                    continue
                if dest_id is None:
                    logger.error(f"Problem with request, no match's image id: {pformat(curr_req_2)}")
                    continue

                if yes_maybe_no_mode:
                    # set threshold depending on Yes/Maybe/No in VisJS
                    # By creatin a fictive distance, depending on the decision
                    fictive_dist = scoring_datastrutures.DecisionTypes.get_fictive_dist(deci)

                    # Add a fictive edge
                    graph.add_edge(Edge(_from=req_id,
                                        _to=dest_id,
                                        color={"color": color_list[i % len(color_list)]},
                                        label=deci + ":" + str(dist),
                                        value=fictive_dist))
                else:
                    graph.add_edge(Edge(_from=req_id,
                                        _to=dest_id,
                                        color={"color": color_list[i % len(color_list)]},
                                        label=deci + ":" + str(dist),
                                        value=dist))

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
    # image_folder = get_homedir() / "datasets" / "MINI_DATASET"
    image_folder = get_homedir() / "datasets" / "raw_phishing_full"
    output_path = get_homedir() / "carlhauser_client"
    evaluator.get_proximity_graph(image_folder, output_path)

    # if __name__ == "__main__":
    #     test()


# Launch a server instance
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch an upload and an evaluation of a list of picture given a ground truth file.')
    parser.add_argument("-s", '--source_path', dest="src", required=True, type=dir_path, action='store',
                        help='Source path of folder of pictures to evaluate. Should be a subset of your production data.')
    parser.add_argument("-gt", '--ground_truth', dest="gt", required=True, type=dir_path, action='store',
                        help='Ground truth file path which has clustered version of the provided data. Very important as it is on what the optimization will based its calculations !')
    parser.add_argument("-d", '--dest_path', dest="dest", required=True, type=dir_path, action='store',
                        help='Destination path to store results of the evaluation (configuration files generated, etc.)')

    args = parser.parse_args()

    evaluator = GraphExtractor()
    evaluator.get_proximity_graph_and_evaluate(pathlib.Path(args.src), pathlib.Path(args.dest), pathlib.Path(args.gt))
