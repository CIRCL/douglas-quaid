#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pathlib

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.Configuration.webservice_conf as webservice_conf
import common.ImportExport.json_import_export as json_import_export
from common.environment_variable import JSON_parsable_Dict
from common.environment_variable import dir_path
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class ConfArgs(JSON_parsable_Dict):
    """
    Specify argument to use to launch workers
    """
    DB_CONF_ARG = '-dbc'
    DB_CONF_NAME = 'db_conf'

    DIST_CONF_ARG = '-distc'
    DIST_CONF_NAME = 'dist_conf'

    FE_CONF_ARG = '-fec'
    FE_CONF_NAME = 'fe_conf'

    WS_CONF_ARG = '-wsc'
    WS_CONF_NAME = 'ws_conf'

    MODE_ARG = '-m'
    MODE_NAME = 'mode'


def add_arg_db_conf(parser: argparse.ArgumentParser):
    parser.add_argument(ConfArgs.DB_CONF_ARG,
                        '--database_configuration_file',
                        dest=ConfArgs.DB_CONF_NAME,
                        type=dir_path,
                        help='DB_configuration_file stored as json. Path')
    return parser


def add_arg_ws_conf(parser: argparse.ArgumentParser):
    parser.add_argument(ConfArgs.WS_CONF_ARG,
                        '--webservice_configuration_file',
                        dest=ConfArgs.WS_CONF_NAME,
                        type=dir_path,
                        help='WebService_configuration_file stored as json. Path')
    return parser


def add_arg_fe_conf(parser: argparse.ArgumentParser):
    parser.add_argument(ConfArgs.FE_CONF_ARG,
                        '--feature_configuration_file',
                        dest=ConfArgs.FE_CONF_NAME,
                        type=dir_path,
                        help='Feature_configuration_file stored as json. Path')
    return parser


def add_arg_dist_conf(parser: argparse.ArgumentParser):
    parser.add_argument(ConfArgs.DIST_CONF_ARG,
                        '--distance_configuration_file',
                        dest=ConfArgs.DIST_CONF_NAME,
                        type=dir_path,
                        help='DIST_configuration_file stored as json. Path')
    return parser


def add_mode(parser: argparse.ArgumentParser):
    parser.add_argument(ConfArgs.MODE_ARG, '--mode',
                        dest=ConfArgs.MODE_NAME,
                        required=True,
                        type=str,
                        choices={"ADD", "REQUEST"},
                        help='Specify queues to work from/to for the worker.')
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

    logger = logging.getLogger()
    tmp_db_conf, tmp_dist_conf, tmp_fe_conf, tmp_ws_conf = None, None, None, None

    # Load the provided configuration file and create back the Configuration Object
    try:
        conf_arg = getattr(args, ConfArgs.DB_CONF_NAME)
        if conf_arg:
            tmp_db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(conf_arg)))
    except AttributeError as e:
        logger.debug(f"No DB CONF argument : {e}. This may be normal if current launch (e.g. a worker) does not require this configuration.")

    try:
        conf_arg = getattr(args, ConfArgs.DIST_CONF_NAME)
        if conf_arg:
            tmp_dist_conf = distance_engine_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(conf_arg)))
    except AttributeError as e:
        logger.debug(f"No DIST CONF argument : {e}. This may be normal if current launch (e.g. a worker) does not require this configuration.")

    try:
        conf_arg = getattr(args, ConfArgs.FE_CONF_NAME)
        if conf_arg:
            tmp_fe_conf = feature_extractor_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(conf_arg)))
    except AttributeError as e:
        logger.debug(f"No FE CONF argument : {e}. This may be normal if current launch (e.g. a worker) does not require this configuration.")

    try:
        conf_arg = getattr(args, ConfArgs.WS_CONF_NAME)
        if conf_arg:
            tmp_ws_conf = webservice_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(conf_arg)))
    except AttributeError as e:
        logger.debug(f"No WS CONF argument : {e}. This may be normal if current launch (e.g. a worker) does not require this configuration.")

    return tmp_db_conf, tmp_dist_conf, tmp_fe_conf, tmp_ws_conf
