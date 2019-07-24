#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, auto
from typing import List

from common.environment_variable import JSON_parsable_Enum
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class DecisionTypes(JSON_parsable_Enum, Enum):
    """
    Possible answer to the question "Are these pictures the same ?"
    """
    YES = auto()
    MAYBE = auto()
    NO = auto()

    @staticmethod
    def get_fictive_dist(decision: str):
        # set threshold depending on Yes/Maybe/No in VisJS
        # By creation a fictive distance, depending on the decision
        if decision == DecisionTypes.YES.name:
            return 0
        elif decision == DecisionTypes.MAYBE.name:
            return 0.5
        elif decision == DecisionTypes.NO.name:
            return 0.75
        else:
            return 1.0  # This is an error if such value is in the final graph


class AlgoMatch:
    """
    Datastructure to handle the returned values of a "distance evaluation" between two hashs, Orb ...
    """

    def __init__(self, name=None, distance=None, decision=None):
        self.name = name
        self.distance = distance
        self.decision = decision

    def to_obj(self):
        tmp_obj = {}
        tmp_obj["name"] = self.name
        tmp_obj["distance"] = self.distance
        tmp_obj["decision"] = self.decision.name

        return tmp_obj

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' name=', self.name,
                                 ' distance=', self.distance,
                                 ' decision=', self.decision]))


#
class ClusterMatch:
    """
    Datastructures to handle a match, a distance/decision, from a picture to a cluster.
    """

    def __init__(self, cluster_id=None, distance=None, decision=None):
        self.cluster_id = cluster_id
        self.distance = distance
        self.decision = decision

    def to_obj(self):
        tmp_obj = {}
        tmp_obj["cluster_id"] = self.cluster_id
        tmp_obj["distance"] = self.distance
        tmp_obj["decision"] = self.decision.name

        return tmp_obj

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' cluster_id=', self.cluster_id,
                                 ' distance=', self.distance,
                                 ' decision=', self.decision]))


class ImageMatch:
    """
    Datastructures to handle a match, a distance/decision, from a picture to another picture.
    """

    def __init__(self, image_id=None, cluster_id=None, distance=None, decision=None):
        self.image_id = image_id
        self.cluster_id = cluster_id
        self.distance = distance
        self.decision = decision

    def to_obj(self):
        tmp_obj = {}
        tmp_obj["image_id"] = self.image_id
        tmp_obj["cluster_id"] = self.cluster_id
        tmp_obj["distance"] = self.distance
        tmp_obj["decision"] = self.decision.name

        return tmp_obj

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' image_id=', self.image_id,
                                 ' cluster_id=', self.cluster_id,
                                 ' distance=', self.distance,
                                 ' decision=', self.decision]))


class TopN:
    """
    Datastructure to handle the top N matches of some type.
    """

    # TODO : Improve datastructure (priority queue, probably)
    def __init__(self, top_n):
        self.list_top_n_elements = []
        self.top_n = top_n
        self.sorted = False

    def add_element(self, element):
        self.list_top_n_elements.append(element)
        self.sorted = False

    def get_top_n(self) -> List:
        # Get the top n of the elements of the list

        # Sort elements if not sorted
        if not self.sorted:
            self.list_top_n_elements.sort(key=lambda x: x.distance)
            self.sorted = True

        # Return the top n elements of the list
        return self.list_top_n_elements[:min(self.top_n, len(self.list_top_n_elements))]


# ==================== ------ BACKGROUND COMPUTATION ------- ====================

def build_response(request_id, list_cluster: List[ClusterMatch], list_pictures: List[ImageMatch]) -> dict:
    results = {}

    # Store request id
    results["request_id"] = request_id

    if len(list_pictures) > 0:
        results["status"] = "matches_found"

        # Store clusters
        tmp_list = [cluster.to_obj() for cluster in list_cluster]
        results["list_cluster"] = tmp_list

        # Store pictures
        tmp_list = [picture.to_obj() for picture in list_pictures]
        results["list_pictures"] = tmp_list
    else:
        results["status"] = "matches_not_found"

    return results
