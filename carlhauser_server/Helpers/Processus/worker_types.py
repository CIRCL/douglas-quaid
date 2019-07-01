#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==================== ------ STD LIBRARIES ------- ====================
from collections import namedtuple
from enum import Enum, auto
# ==================== ------ PERSONAL LIBRARIES ------- ====================

from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum


class WorkerTypes(JSON_parsable_Enum, Enum):
    ADDER = auto()
    REQUESTER = auto()
    FEATURE_ADDER = auto()
    FEATURE_REQUESTER = auto()
    FLASK = auto()
