#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==================== ------ STD LIBRARIES ------- ====================
from enum import Enum, auto

from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum


# ==================== ------ PERSONAL LIBRARIES ------- ====================


class WorkerTypes(JSON_parsable_Enum, Enum):
    ADDER = auto()
    REQUESTER = auto()
    FEATURE_ADDER = auto()
    FEATURE_REQUESTER = auto()
    FLASK = auto()
