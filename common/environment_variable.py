#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import logging
import logging.config

# ==================== ------ PERSONAL LIBRARIES ------- ====================
 


# ============================ HOME DIR GETTER ============================

def get_homedir() -> pathlib.Path:
    if not os.environ.get('CARLHAUSER_HOME'):
        guessed_home = pathlib.Path(__file__).resolve().parent.parent
        raise Exception(f"CARLHAUSER_HOME is missing. Run the following command (assuming you run the code from the cloned repository):\nexport CARLHAUSER_HOME='{guessed_home}'")
    return pathlib.Path(os.environ['CARLHAUSER_HOME'])

def load_client_logging_conf_file():
    # load the logging configuration
    logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
    logging.config.fileConfig(str(logconfig_path))
# FORMATTER = logging.Formatter('%(asctime)s - + %(relativeCreated)d - %(name)s - %(levelname)s - %(message)s')

def load_server_logging_conf_file():
    # load the logging configuration
    logconfig_path = (get_homedir() / pathlib.Path("carlhauser_server", "logging.ini")).resolve()
    logging.config.fileConfig(str(logconfig_path))

def make_big_line():
    return "======================================================================================="

def make_small_line():
    return "---------------------------------------------------------------------------------------"


# ============================ STATIC UTILITIES ============================

def dir_path(path):
    if pathlib.Path(path).exists():
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def resolve_path(file_path: pathlib.Path) -> pathlib.Path:
    '''
    If the provided path is not absolute, resolve it. Otherwise, do nothing
    :param file_path: the filepath to resolve
    :return: the absolute path
    '''
    # Solve the file path
    if not file_path.is_absolute():
        file_path = file_path.resolve()
    return file_path


# ============================ STATIC VALUES ============================

class JSON_parsable_Dict:
    pass


class JSON_parsable_Enum:
    pass


class QueueNames(JSON_parsable_Dict):
    FEATURE_TO_ADD = "feature_to_add"
    FEATURE_TO_REQUEST = "feature_to_request"
    DB_TO_ADD = "db_to_add"
    DB_TO_REQUEST = "db_to_request"


class EndPoints(JSON_parsable_Dict):
    # PING = "ping"
    ADD_PICTURE = "add_picture"
    WAIT_FOR_ADD = "wait_for_add"
    REQUEST_PICTURE = "request_similar_picture"  # "request_picture"
    WAIT_FOR_REQUEST = "is_ready"  # "wait_for_request"
    GET_REQUEST_RESULT = "get_results"
    REQUEST_DB = "export_db"

