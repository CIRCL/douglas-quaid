#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
from typing import List, Set

from common.environment_variable import JSON_parsable_Dict
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class ComputationTime(JSON_parsable_Dict):
    def __init__(self):
        # Time
        self.feature_time: float = None
        self.adding_time: float = None
        self.request_time: float = None
        # Amount
        self.nb_picture_added: int = None
        self.nb_picture_total_in_db: int = None
        self.nb_picture_requested: int = None
        self.iteration: int = None

    def get_sum(self):
        return self.feature_time if not None else 0 + self.adding_time if not None else 0 + self.request_time if not None else 0

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' \nfeature_time=', self.feature_time,
                                 ' \nadding_time=', self.adding_time,
                                 ' \nrequest_time=', self.request_time,
                                 ' \nnb_picture_added=', self.nb_picture_added,
                                 ' \nnb_picture_requested=', self.nb_picture_requested,
                                 ' \niteration=', self.iteration]))


class ScalabilityData(JSON_parsable_Dict):
    def __init__(self):
        # self.response_time: float = None
        self.threshold_cluster = None

        # Request time of each
        self.list_request_time: List[ComputationTime] = []

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' \nlist_request_time=', self.list_request_time]))


# Tricky construction to make the API believe we are passing a flder of pictures
class Pathobject(pathlib.PosixPath):
    def is_file(self):
        return True


class PathlibSet():
    def __init__(self, myset: Set):
        self.set = myset

    def iterdir(self):
        return list(self.set)
