#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import pathlib
from typing import List

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from common.Graph.cluster import Cluster
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


class ConfusionMatrixGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.ord = None
        self.abs = None
        self.values = None

    # ============================== ---- Creation of matrix ----  ==============================

    def create_and_export_confusion_matrix(self, original: List[Cluster],
                                           candidate: List[Cluster],
                                           save_path: pathlib.Path = None):
        """
        Create and export a confusion matrix from two list of clusters. The confusion matrix display the number of pictures in common between any pair of two cluster, taken in both lists.
        :param original: a List of cluster with their members
        :param candidate: a List of cluster with their members
        :param save_path: the path to which the matrix PDF) will be stored
        :return: Nothing
        """

        self.logger.debug(f"Create and export confusion matrix, inputs : original = {original} ; candidate = {candidate}")

        # Sort arrays (bigger to smaller)
        original.sort(key=lambda x: len(x.members), reverse=True)
        candidate.sort(key=lambda x: len(x.members), reverse=True)

        self.logger.debug(f"Sorted : {original} {candidate}")

        # Creation of the axis values
        ordo, absi, values = [], [], []

        # Create label printed on each axis
        for gt_cluster in original:
            ordo.append(''.join([str(gt_cluster.label), " (#", str((len(gt_cluster.members))), ")", ]))

        for cand in candidate:
            absi.append(''.join([str(cand.label), " (#", str((len(cand.members))), ")", ]))

        # Generate values
        for row, gt_cluster in enumerate(original):
            tmp_row_values = []
            for col, cand in enumerate(candidate):
                # Compute intersection = True positive or False Positive (as we don't know if that's a "good" cluster)
                intersect = len(gt_cluster.members.intersection(cand.members))
                tmp_row_values.append(intersect)
            values.append(tmp_row_values)

        # TODO : Color if matched on this attribute ?

        self.set_values(ordo, absi, values)
        self.save_matrix(save_path.with_suffix(".pdf"))

    # ============================== ---- Utility ----  ==============================

    def set_values(self, ordo, absi, values):
        self.ord = ordo
        self.abs = absi
        self.values = np.array(values)

    def save_matrix(self, output_file: pathlib.Path):
        """
        Create a matrix (a picture/chart) with specific size, etc.
        :param output_file: The path where to save the matrix picture.
        :return: Nothing
        """
        fig, ax = plt.subplots(figsize=(20, 14), dpi=200)

        im, cbar = self.heatmap(self.values, self.ord, self.abs, ax=ax,
                                cmap="YlGn", cbarlabel="Nb of elements in these clusters")
        texts = self.annotate_heatmap(im, data=self.values, valfmt="{x:.1f}")

        fig.tight_layout()
        plt.savefig(str(output_file))

    # ============================== --------------------------------  ==============================
    #                                   Graphical operation

    @staticmethod
    def heatmap(data, row_labels, col_labels, ax=None, cbar_kw={}, cbarlabel="", **kwargs):
        """
        Create a heatmap from a numpy array and two lists of labels.

        Arguments:
            data       : A 2D numpy array of shape (N,M)
            row_labels : A list or array of length N with the labels
                         for the rows
            col_labels : A list or array of length M with the labels
                         for the columns
        Optional arguments:
            ax         : A matplotlib.axes.Axes instance to which the heatmap
                         is plotted. If not provided, use current axes or
                         create a new one.
            cbar_kw    : A dictionary with arguments to
                         :param ax:
                         :meth:`matplotlib.Figure.colorbar`.
            cbarlabel  : The label for the colorbar
        All other arguments are directly passed on to the imshow call.
        """

        if not ax:
            ax = plt.gca()

        # TRICK TO DO MAX PER ROW
        normalized_data = data.copy()
        row_sums = normalized_data.sum(axis=1)
        '''
        print(type(row_sums))
        print(normalized_data)
        print(row_sums)
        print(row_sums[:, np.newaxis])
        '''
        normalized_data = normalized_data / row_sums[:, np.newaxis]
        # data = data.div(data.max(axis=1), axis=0)

        # Plot the heatmap
        im = ax.imshow(normalized_data, **kwargs)

        # Create colorbar
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

        # We want to show all ticks...
        ax.set_xticks(np.arange(data.shape[1]))
        ax.set_yticks(np.arange(data.shape[0]))
        # ... and label them with the respective list entries.
        ax.set_xticklabels(col_labels)
        ax.set_yticklabels(row_labels)

        # Let the horizontal axes labeling appear on top.
        ax.tick_params(top=True, bottom=False,
                       labeltop=True, labelbottom=False)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
                 rotation_mode="anchor")

        # Turn spines off and create white grid.
        for edge, spine in ax.spines.items():
            spine.set_visible(False)

        ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
        ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)
        # ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
        ax.tick_params(which="minor", bottom=False, left=False)

        return im, cbar

    @staticmethod
    def annotate_heatmap(im, data=None, valfmt="{x:.2f}", textcolors=["black", "white"], threshold=None, **textkw):
        """
        A function to annotate a heatmap.

        Arguments:
            im         : The AxesImage to be labeled.
        Optional arguments:
            data       : Data used to annotate. If None, the image's data is used.
            valfmt     : The format of the annotations inside the heatmap.
                         This should either use the string format method, e.g.
                         "$ {x:.2f}", or be a :class:`matplotlib.ticker.Formatter`.
            textcolors : A list or array of two color specifications. The first is
                         used for values below a threshold, the second for those
                         above.
            threshold  : Value in data units according to which the colors from
                         textcolors are applied. If None (the default) uses the
                         middle of the colormap as separation.

        Further arguments are passed on to the created text labels.
        """

        if not isinstance(data, (list, np.ndarray)):
            data = im.get_array()

        # Normalize the threshold to the images color range.
        if threshold is not None:
            threshold = im.norm(threshold)
        else:
            threshold = im.norm(data.max()) / 2.

        # Set default alignment to center, but allow it to be
        # overwritten by textkw.
        kw = dict(horizontalalignment="center",
                  verticalalignment="center")
        kw.update(textkw)

        # Get the formatter in case a string is supplied
        if isinstance(valfmt, str):
            valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

        # Loop over the data and create a `Text` for each "pixel".
        # Change the text's color depending on the data.
        texts = []
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                kw.update(color=textcolors[im.norm(data[i, j]) > threshold])
                text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
                texts.append(text)

        return texts
