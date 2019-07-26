#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pathlib
import time
from typing import List, Set

import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import common.ChartMaker.two_dimensions_plot as two_dimensions_plot
import common.ImportExport.json_import_export as json_import_export
import common.Scalability_evaluator.scalability_conf as scalability_conf
import common.TestInstanceLauncher.one_db_conf as test_database_only_conf
import common.TestInstanceLauncher.one_db_instance_launcher as test_database_handler
from carlhauser_client.API.extended_api import Extended_API
from common.Scalability_evaluator.scalability_datastructures import ScalabilityData, ComputationTime, PathlibSet, Pathobject
from common.environment_variable import dir_path
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class ScalabilityEvaluator:

    def __init__(self, tmp_scalability_conf=scalability_conf.Default_scalability_conf()):
        self.logger = logging.getLogger()
        self.ext_api: Extended_API = Extended_API.get_api()

        # self.test_db_handler: test_database_handler.TestInstanceLauncher = None
        print(tmp_scalability_conf)
        self.scalability_conf: scalability_conf.Default_scalability_conf = tmp_scalability_conf

    def load_pictures(self, pictures_folder: pathlib.Path) -> Set[pathlib.Path]:
        pictures_set = set()

        # Load all path to pictures in a set
        for x in pictures_folder.resolve().glob('**/*'):  # pictures_folder.resolve().iterdir():
            if x.is_file():
                pictures_set.add(Pathobject(x))

        return pictures_set

    def evaluate_scalability(self,
                             pictures_folder: pathlib.Path,
                             output_folder: pathlib.Path) -> ScalabilityData:

        # ==== Separate the folder files ====
        pictures_set = self.load_pictures(pictures_folder)

        # Extract X pictures to evaluate their matching (at each cycle, the sames)
        pictures_set, pics_to_evaluate = self.biner(pictures_set, self.scalability_conf.NB_PICS_TO_REQUEST)

        # Put TOTAL-X pictures into boxes (10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000 ...)
        # Generate the boxes
        list_boxes_sizes = self.scalability_conf.generate_boxes(self.scalability_conf.MAX_NB_PICS_TO_SEND)

        # ==== Upload pictures + Make requests ====
        scalability_data = self.get_scalability_list(list_boxes_sizes, pictures_set, pics_to_evaluate)

        self.logger.info(f"Scalability data : {scalability_data}")
        self.print_data(scalability_data, output_folder)

        return scalability_data

    def get_scalability_list(self, list_boxes_sizes: List[int], pictures_set: Set[pathlib.Path], pics_to_evaluate: Set[pathlib.Path],
                             dist_conf: distance_engine_conf.Default_distance_engine_conf = distance_engine_conf.Default_distance_engine_conf(),
                             fe_conf: feature_extractor_conf.Default_feature_extractor_conf = feature_extractor_conf.Default_feature_extractor_conf()
                             ):
        # ==== Upload pictures + Make requests ====
        scalability_data = ScalabilityData()

        # For each box
        for i, curr_box_size in enumerate(list_boxes_sizes):
            # Get a list of pictures to send
            pictures_set, pics_to_store = self.biner(pictures_set, curr_box_size)

            # If we are not out of pictures to send
            if len(pics_to_store) != 0:
                # Evaluate time for this database size and store it
                tmp_scal_datastruct = self.evaluate_scalability_lists(list_pictures_eval=pics_to_evaluate,
                                                                      list_picture_to_up=pics_to_store,
                                                                      tmp_id=i,
                                                                      dist_conf=dist_conf,
                                                                      fe_conf=fe_conf)
                scalability_data.list_request_time.append(tmp_scal_datastruct)

        return scalability_data

    def evaluate_scalability_lists(self,
                                   list_pictures_eval: Set[pathlib.Path],
                                   list_picture_to_up: Set[pathlib.Path],
                                   tmp_id: int,
                                   dist_conf: distance_engine_conf.Default_distance_engine_conf = distance_engine_conf.Default_distance_engine_conf(),
                                   fe_conf: feature_extractor_conf.Default_feature_extractor_conf = feature_extractor_conf.Default_feature_extractor_conf()) -> ComputationTime:

        db_conf = test_database_only_conf.TestInstance_database_conf()  # For test sockets only

        # Launch a modified server
        self.logger.debug(f"Creation of a full instance of redis (Test only) ... ")

        test_db_handler = test_database_handler.TestInstanceLauncher()

        test_db_handler.create_full_instance(db_conf=db_conf, dist_conf=dist_conf, fe_conf=fe_conf)

        # Tricky tricky : create a fake Pathlib folder to perform the upload
        self.logger.debug(f"Faking pathlib folders ... ")
        simulated_folder_add = PathlibSet(list_picture_to_up)
        simulated_folder_request = PathlibSet(list_pictures_eval)

        # Time Management - Start
        start_upload = time.time()

        # Upload pictures of one bin
        self.logger.debug(f"Sending pictures ... ")
        _, nb_pictures_add = self.ext_api.add_many_pictures_and_wait_global(simulated_folder_add)

        # Time Management - Stop
        stop_upload = abs(start_upload - time.time())
        self.logger.info(f"Upload of {nb_pictures_add} took {stop_upload}s, so {stop_upload / nb_pictures_add if nb_pictures_add != 0 else 1}s per picture.")

        # Time Management - Start
        start_request = time.time()

        # Make request of the X standard pictures
        self.logger.debug(f"Requesting pictures ... ")
        _, nb_pictures_req = self.ext_api.request_many_pictures_and_wait_global(simulated_folder_request)

        # Time Management - Stop
        stop_request = abs(start_request - time.time())
        self.logger.info(f"Request of {nb_pictures_req} took {stop_request}s, so {stop_request / nb_pictures_req if nb_pictures_req != 0 else 1}s per picture.")

        # Construct storage object = Store the request times
        resp_time = ComputationTime()
        resp_time.adding_time = stop_upload
        resp_time.request_time = stop_request
        resp_time.nb_picture_added = len(list_picture_to_up)
        resp_time.nb_picture_requested = len(list_pictures_eval)
        resp_time.iteration = tmp_id

        # Kill server instance
        self.logger.debug(f"Shutting down Redis test instance")
        test_db_handler.tearDown()

        return resp_time

    @staticmethod
    def biner(potential_pictures: Set[pathlib.Path], nb_to_bin):
        # Extract <nbtobin> pitures from the provided set. Return both modified set and bin
        bin_set = set()

        for i in range(min(nb_to_bin, len(potential_pictures))):
            bin_set.add(potential_pictures.pop())

        return potential_pictures, bin_set

    def print_data(self, scalabilitygraph: ScalabilityData, output_folder: pathlib.Path, file_name: str = "scalability_graph.pdf"):
        twoDplot = two_dimensions_plot.TwoDimensionsPlot()
        twoDplot.print_scalability_data(scalabilitygraph, output_folder, file_name)

        # Save to file
        json_import_export.save_json(scalabilitygraph.list_request_time, output_folder / "scalability_graph.json")
        self.logger.info("Results scalability_graph json saved.")


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch DouglasQuaid Scalability Evaluator on your own dataset to get custom scalability measure')
    parser.add_argument("-s", '--source_path', dest="src", required=True, type=dir_path, action='store',
                        help='Source path of folder of pictures to evaluate. Should be a subset of your production data.')
    parser.add_argument("-d", '--dest_path', dest="dest", required=True, type=dir_path, action='store',
                        help='Destination path to store results of the evaluation (configuration files generated, etc.)')
    args = parser.parse_args()

    try:
        scalability_evaluator = ScalabilityEvaluator()
        scalability_evaluator.evaluate_scalability(pathlib.Path(args.src), pathlib.Path(args.dest))

    except AttributeError as e:
        parser.error(f"Too few arguments : {e}")
