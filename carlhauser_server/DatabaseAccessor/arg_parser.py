#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import argparse
import os
import pathlib
import sys

# ==================== ------ PERSONAL LIBRARIES ------- ====================
import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import common.ImportExport.json_import_export as json_import_export
from common.environment_variable import dir_path

sys.path.append(os.path.abspath(os.path.pardir))


def add_arg_db_conf(parser : argparse.ArgumentParser) :
    parser.add_argument("-dbc", '--configuration_file', dest="db_conf", type=dir_path, help='DB_configuration_file stored as json. Path')
    return parser

def add_arg_ws_conf(parser : argparse.ArgumentParser) :
    parser.add_argument("-wsc", '--webservice_configuration_file', dest="ws_conf", type=dir_path, help='WebService_configuration_file stored as json. Path')
    return parser

def add_arg_fe_conf(parser : argparse.ArgumentParser) :
    parser.add_argument("-fec", '--feature_configuration_file', dest="fe_conf", type=dir_path, help='Feature_configuration_file stored as json. Path')
    return parser

def add_arg_dist_conf(parser : argparse.ArgumentParser) :
    parser.add_argument("-distc", '--distance_configuration_file', dest="dist_conf", type=dir_path, help='DIST_configuration_file stored as json. Path')
    return parser

def add_mode(parser : argparse.ArgumentParser) :
    parser.add_argument("-m", '--mode', dest="mode", required=True, type=str, choices={"ADD", "REQUEST"}, help='Specify queues to work from/to for the worker.')
    return parser

def parse_conf_files(args) -> (database_conf.Default_database_conf,
                               distance_engine_conf.Default_distance_engine_conf,
                               feature_extractor_conf.Default_feature_extractor_conf,
                               webservice_conf.Default_webservice_conf):
    """
    Parse args to configuration files, if they exist.
    Usage example : db_conf, dist_conf, fe_conf, ws_conf = arg_parser.parse_conf_files(args)
    :param args: parsed arguments from command line
    :return: db_conf, dist_conf, feature_conf, webservice_conf
    """

    tmp_db_conf, tmp_dist_conf, tmp_fe_conf, tmp_ws_conf = None, None, None, None

    # Load the provided configuration file and create back the Configuration Object
    if args.db_conf :
        tmp_db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.db_conf)))
    if args.dist_conf :
        tmp_dist_conf = distance_engine_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.dist_conf)))
    if args.fe_conf :
        tmp_fe_conf = feature_extractor_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.fe_conf)))
    if args.ws_conf :
        tmp_ws_conf = webservice_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.ws_conf)))

    return tmp_db_conf, tmp_dist_conf, tmp_fe_conf, tmp_ws_conf





