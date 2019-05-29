#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

from typing import List
from pprint import pformat

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
from common.Graph.graph_datastructure import GraphDataStruct
from common.Graph.metadata import Metadata, Source
from common.Graph.cluster import Cluster
from common.Graph.edge import Edge
from common.Graph.node import Node
# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class Scoring():

    def __init__(self):
        # Lost ? Go there : https://en.wikipedia.org/wiki/Sensitivity_and_specificity
        self.P = None  # condition positive (P)
        self.N = None  # condition negative (N)

        self.TP = None  # true positive (TP)
        self.FP = None  # true negative (TN)
        self.TN = None  # false positive (FP)
        self.FN = None  # false negative (FN)

        self.TPR = None  # sensitivity, recall, hit rate, or true positive rate (TPR)
        self.TNR = None  # specificity, selectivity or true negative rate (TNR)

        self.PPV = None  # precision or positive predictive value (PPV)
        self.NPV = None  # negative predictive value (NPV)

        self.FNR = None  # miss rate or false negative rate (FNR)
        self.FPR = None  # fall-out or false positive rate (FPR)

        self.FDR = None  # false discovery rate (FDR)
        self.FOR = None  # false omission rate (FOR)

        self.ACC = None  # accuracy (ACC)
        self.F1 = None  # F1 score
        self.MCC = None  # Matthews correlation coefficient (MCC)
        self.BM = None  # Informedness or Bookmaker Informedness (BM)
        self.MK = None  # Markedness (MK)

    def compute_TPR(self):
        self.TPR = self.TP / self.P

    def compute_TNR(self):
        self.TNR = self.TN / self.N

    def compute_PPV(self):
        self.PPV = self.TP / (self.TP + self.FP)

    def compute_NPV(self):
        self.NPV = self.TN / (self.TN + self.FN)

    def compute_FNR(self):
        self.FNR = self.FN / self.P

    def compute_FPR(self):
        self.FPR = self.FP / self.N

    def compute_FDR(self):
        self.FDR = self.FP / (self.FP + self.TP)

    def compute_FOR(self):
        self.FOR = self.FN / (self.FN + self.TN)

    def compute_ACC(self):
        self.ACC = (self.TP + self.TN) / (self.P + self.N)

    def compute_F1(self):
        self.F1 = (2 * self.TP) / (2 * self.TP + self.FP + self.FN)

    def check_sanity(self):
        try:
            assert (self.P == self.FN + self.TP)
            assert (self.N == self.FN + self.TP + self.FP)
            assert (self.N <= self.TN)
            assert (self.P >= self.TP)

            return True
        except Exception as e:
            return False

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):

        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, ['P=', self.P, ' N=', self.N,
                                 ' ACC=', self.ACC, ' F1=', self.F1,
                                 ' TP=', self.TP, ' TN=', self.TN,
                                 ' FP=', self.FP, ' FN=', self.FN]))

