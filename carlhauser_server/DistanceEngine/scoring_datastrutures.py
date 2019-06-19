#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
from typing import List
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict
from enum import Enum, auto

# ==================== ------ PERSONAL LIBRARIES ------- ====================

class DecisionTypes(JSON_parsable_Enum, Enum):
    # Possible answer to the question "Are these pictures the same ?"
    YES = auto()
    MAYBE = auto()
    NO = auto()

class AlgoMatch :
    # Datastructure to handle the returned values of a "distance evaluation" between two hashs, Orb ...
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

# Datastructures to handle a list of matches
class ClusterMatch:
    def __init__(self, cluster_id=None, distance=None):
        self.cluster_id = cluster_id
        self.distance = distance

    def to_obj(self):
        tmp_obj = {}
        tmp_obj["cluster_id"] = self.cluster_id
        tmp_obj["distance"] = self.distance
        return tmp_obj

class ImageMatch:
    def __init__(self, image_id=None, cluster_id=None, distance=None):
        self.image_id = image_id
        self.cluster_id = cluster_id
        self.distance = distance

    def to_obj(self):
        tmp_obj = {}
        tmp_obj["image_id"] = self.image_id
        tmp_obj["cluster_id"] = self.cluster_id
        tmp_obj["distance"] = self.distance
        return tmp_obj

class TopN:
    # TODO : Improve datastructure (priority queue, probably)
    def __init__(self, top_n):
        self.list_top_n_elements = []
        self.top_n = top_n
        self.sorted = False

    def add_element(self, element):
        self.list_top_n_elements.append(element)
        self.sorted = False

    def get_top_n(self):
        # Get the top n of the elements of the list

        # Sort elements if not sorted
        if not self.sorted:
            self.list_top_n_elements.sort(key=lambda x: x.distance)
            self.sorted = True

        # Return the top n elements of the list
        return self.list_top_n_elements[:min(self.top_n, len(self.list_top_n_elements))]

# ==================== ------ BACKGROUND COMPUTATION ------- ====================

def build_response(request_id, list_cluster : List[ClusterMatch], list_pictures: List[ImageMatch]) -> dict:
    results = {}

    # Store request id
    results["request_id"] = request_id

    if len(list_pictures) > 0 :
        results["status"] = "matches_found"

        # Store clusters
        tmp_list = [cluster.to_obj() for cluster in list_cluster]
        results["list_cluster"] = tmp_list

        # Store pictures
        tmp_list = [picture.to_obj() for picture in list_pictures]
        results["list_pictures"] = tmp_list
    else :
        results["status"] = "matches_not_found"

    return results