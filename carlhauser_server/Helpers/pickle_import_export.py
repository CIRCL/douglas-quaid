#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import pathlib
import logging
import json
import base64
import pickle
import _pickle as cPickle

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


def get_object_from_pickle(pickle_obj):
    # Return an object from the pickle version of it

    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    return cPickle.loads(pickle_obj)


def get_pickle_from_object(obj):
    # Return a pickle version of an object

    # Pickle the 'data' dictionary using the highest protocol available = the faster (>json since v3)
    return cPickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)





