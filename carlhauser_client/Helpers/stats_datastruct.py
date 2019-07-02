#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

from typing import List, Set

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================
class Stats_datastruct:

    def __init__(self):
        # Lost ? Go there : https://en.wikipedia.org/wiki/Sensitivity_and_specificity
        self.P = None  # condition positive (P)
        self.N = None  # condition negative (N)

        self.total_nb_elements = None

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

    def compute_all(self, truth_set: Set, candidate_set: Set, total_nb_elements):
        # Compute all possible metrics, given information provided

        # Store nb of elements in total
        self.total_nb_elements = total_nb_elements

        # Get number of "true element" in the dataset
        self.P = len(truth_set)

        # Compute true positive as intersection of ground truth and candidate clusters
        intersect = truth_set.intersection(candidate_set)
        self.TP = len(intersect)

        # Compute False Positive as what is in candidate but not in ground truth (and so the intersection)
        only_in_candidate = candidate_set.difference(intersect)
        self.FP = len(only_in_candidate)

        # Compute False Negative as what is in ground truth but not in candidate (and so the intersection)
        only_in_ground_truth = truth_set.difference(intersect)
        self.FN = len(only_in_ground_truth)

        # Diverse other metrics
        self.compute_TPR()
        self.compute_PPV()
        self.compute_FDR()

        if self.total_nb_elements is None:
            raise Exception("Can't compute True Negative rate : we don't know number of all elements in the system.")
        else:
            # Compute True negative as all elements not in the three previous sets
            self.TN = self.total_nb_elements - self.TP - self.FP - self.FN

            # Compute number of negative elements in dataset
            self.N = self.total_nb_elements - len(truth_set)

            # Diverse other metrics
            self.compute_TNR()
            self.compute_NPV()

            self.compute_FNR()
            self.compute_FPR()

            self.compute_FOR()

            self.compute_ACC()
            self.compute_F1()

        self.check_sanity()

    def check_sanity(self):
        try:
            if not (self.P == self.FN + self.TP): raise Exception("Positives != False negative + true positive")
            if not (self.N == self.FN + self.TP + self.FP): raise Exception("Negatives != False negative + true positive + False positive")
            if not (self.N <= self.TN): raise Exception("Negatives !<= True negatives")
            if not (self.P >= self.TP): raise Exception("Positives !>= True positives")

            return True
        except Exception as e:
            return False

    # Operator overwrite
    # TODO : Review ">" operator
    def __gt__(self, other):
        if self.ACC is None or self.F1 is None or other.F1 is None or other.ACC is None:
            # Null scores can be "greater"
            return True
        elif self.ACC > other.ACC and self.F1 > other.F1:
            return True
        else:
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
                                 ' FP=', self.FP, ' FN=', self.FN,
                                 ' TPR=', self.TPR, ' TNR=', self.TNR,
                                 ' PPV=', self.PPV, ' NPV=', self.NPV,
                                 ' FNR=', self.FNR, ' FPR=', self.FPR]))


def merge_scores(scores: List[Stats_datastruct]):
    # Create a "mean score" out of a list of scores

    total_score = Stats_datastruct()

    if scores is not None and len(scores) > 0:
        # Iterate over attributes
        for key in vars(scores[0]):
            # Creation of a list of all "same attribute" for all scores of the list
            tmp = [v for v in (vars(score)[key] for score in scores) if v is not None]
            if len(tmp) > 0:
                # Get the mean
                vars(total_score)[key] = sum(tmp) / len(tmp)

    return total_score
