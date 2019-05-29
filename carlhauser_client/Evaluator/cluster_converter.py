#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir

from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
from common.Graph.metadata import Metadata, Source

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================

class Cluster_converter():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def convert_dump_to_clusters(self, dump_json: dict):
        # Convert the "db" parameter value returned by the server when "dump db" is called.

        # Split raw values per category
        clusters = dump_json["clusters"]
        edges = dump_json["edges"]
        nodes = dump_json["nodes"]

        # Create a cluster dict, stored per id
        clusters_dict = {c["id"]: Cluster(c["id"], c["id"], set()) for c in clusters}

        # Create a node dict, stored per id
        nodes_dict = {n["id"]: n for n in nodes}

        # Iterate on edges, and add each node to the set of the cluster it is linked to
        for e in edges:
            if clusters_dict[e["from"]] and nodes_dict[e["to"]]:
                # Complete : clusters_dict[e["from"]].members.add(nodes_dict[e["to"]]["id"])
                # Note : would need Node object to store more information
                clusters_dict[e["from"]].members.add(e["to"])  # Faster
            else:
                self.logger.error(f"Node or cluster node found. Problem in json consistency : {e['from']}={clusters_dict[e['from']]} {e['to']}={nodes_dict[e['to']]}")

        return list(clusters_dict.values())

    def convert_visjs_to_clusters(self, visjs_json: dict):
        # Convert the graph returned by the visjs

        # Split raw values per category
        clusters = visjs_json["classes"]
        nodes = visjs_json["nodes"]

        # Create a cluster dict, stored per id
        clusters_dict = {c["label"]: Cluster(c["label"], c["label"], set(c["members"])) for c in clusters}

        return list(clusters_dict.values())

    def convert_names_old_to_new(self, mapping_old_to_new : dict, visjs_json: dict):
        # Convert the graph returned by the visjs

        # Split raw values per category
        clusters = visjs_json["classes"]
        nodes = visjs_json["nodes"]

        # ==== Transform mapping filename=>new_id to old_id=> new_id
        mapping_id_to_new_id = {}
        for node in nodes :
            try :
                # Get new id from mapping ...
                new_id = mapping_old_to_new[node["image"]]
                # ... and store to a new mapping : node.id to new_id
                mapping_id_to_new_id[node["id"]] = new_id
                # And replace old id by new id
                node["id"] = new_id
            except Exception as e :
                self.logger.warning(f"Key {node['image']} not in mapping")

        # Create mapping node_label => node_id
        node_label_to_id = {}
        for n in nodes :
            try :
                node_label_to_id[n["label"]] = n["id"]
            except Exception as e:
                continue

        for cluster in clusters :
            tmp_new_members = []
            # Overwrite clusters elements
            for node_id in cluster["members"] :
                # Replace all reference to old id to new id
                tmp_new_members.append(mapping_id_to_new_id[node_id])
                # Overwrite the old list of members
            cluster["members"] = tmp_new_members
            # Overwrite cluster id by original id


        # Merge back
        visjs_json["classes"] = clusters
        visjs_json["nodes"] = nodes

        return visjs_json

    def convert_mapping_to_visjs(self, visjs_original, clusters_pairs: List[List[Cluster]]):

        self.logger.debug(f"clusters_pairs : {clusters_pairs}")

        visjs_json = {}

        classes = []
        nodes = []
        edges = []

        node_set = set({})

        node_dict = { node["id"]:node for node in visjs_original["nodes"]}

        for pair in clusters_pairs:
            truth = pair[0]
            candidate = pair[1]

            self.logger.debug(f"Curr truth : {truth}")
            self.logger.debug(f"Curr candidate : {candidate}")

            # Compute intersection of ground truth and candidate clusters
            intersect = truth.members.intersection(candidate.members)

            # Compute  what is in candidate but not in ground truth (and so the intersection)
            only_in_candidate = candidate.members.difference(intersect)

            # Compute  what is in ground truth but not in candidate (and so the intersection)
            only_in_ground_truth = truth.members.difference(intersect)

            # Add class (matched class)
            tmp_class = {}
            tmp_class["label"] = ''.join(['truth:', truth.label, ' -> created:', candidate.label])
            tmp_class["id"] = ''.join(['truth:', truth.id, ' -> created:', candidate.id])
            classes.append(tmp_class)

            # Change the id of the cluster in the node list
            # TODO : HERE ! TO REVIEW ! node_dict[candidate.id]["id"] = tmp_class["id"]

            # Store all nodes
            node_set = node_set.union(truth.members)
            # Not necessary ? node_set.union(candidate.members)

            #  ==== Create edges ====
            # Edges that are in both group are correctly classified
            for node in intersect :
                tmp_edge = {}
                tmp_edge["from"] = tmp_class["id"]
                tmp_edge["to"] = node # TODO : .id
                tmp_edge["color"] = "gray"
                edges.append(tmp_edge)

            # Edges that are only in candidate are "new"
            for node in only_in_candidate :
                tmp_edge = {}
                tmp_edge["from"] = tmp_class["id"]
                tmp_edge["to"] = node# TODO : .id
                tmp_edge["color"] = "red"
                edges.append(tmp_edge)

            # Edges that are only in ground truth are "missed"
            for node in only_in_ground_truth :
                tmp_edge = {}
                tmp_edge["from"] = tmp_class["id"]
                tmp_edge["to"] = node# TODO : .id
                tmp_edge["color"] = "yellow"
                edges.append(tmp_edge)


        nodes = list(node_dict.values())


        '''
        # Add all nodes to graph
        for node in node_dict:
            # nodes.append({"id":node.id, "shape":"image", "image":node.img_path})
            nodes.append(node_dict.values())
        '''

        # Final json
        visjs_json["classes"] = classes
        visjs_json["nodes"] = nodes
        visjs_json["edges"] = edges

        return visjs_json
