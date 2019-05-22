#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
# ==================== ------ PERSONAL LIBRARIES ------- ====================

# Datastructures to handle a list of matches
class ClusterMatch:
    def __init__(self, cluster_id=None, distance=None):
        self.cluster_id = cluster_id
        self.distance = distance


class ImageMatch:
    def __init__(self, image_id=None, cluster_id=None, distance=None):
        self.image_id = image_id
        self.cluster_id = cluster_id
        self.distance = distance


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
