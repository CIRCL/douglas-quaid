#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import _pickle as cPickle
import copyreg
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pickle
import sys

import cv2

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
import carlhauser_server.Helpers.template_singleton as template_singleton

class Pickler(metaclass=template_singleton.Singleton):

    def __init__(self):
        self.patch_Keypoint_pickiling()

    def patch_Keypoint_pickiling(self):
        # Create the bundling between class and arguements to save for Keypoint class
        # See : https://stackoverflow.com/questions/50337569/pickle-exception-for-cv2-boost-when-using-multiprocessing/50394788#50394788
        def _pickle_keypoint(keypoint): #  : cv2.KeyPoint
            return cv2.KeyPoint, (
                keypoint.pt[0],
                keypoint.pt[1],
                keypoint.size,
                keypoint.angle,
                keypoint.response,
                keypoint.octave,
                keypoint.class_id,
            )
        # C++ : KeyPoint (float x, float y, float _size, float _angle=-1, float _response=0, int _octave=0, int _class_id=-1)
        # Python: cv2.KeyPoint([x, y, _size[, _angle[, _response[, _octave[, _class_id]]]]]) → <KeyPoint object>

        # Apply the bundling to pickle
        copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoint)

    # non static, to be sure we patched it before use, only once
    def get_object_from_pickle(self, pickle_obj):
        # Return an object from the pickle version of it

        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        return cPickle.loads(pickle_obj)

    # non static, to be sure we patched it before use, only once
    def get_pickle_from_object(self, obj):
        # Return a pickle version of an object

        # Pickle the 'data' dictionary using the highest protocol available = the faster (>json since v3)
        return cPickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)





