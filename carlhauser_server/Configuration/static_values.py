# ==================== ------ STD LIBRARIES ------- ====================
import os
import sys
from collections import namedtuple
from enum import Enum, auto
from typing import List

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import JSON_parsable_Enum, JSON_parsable_Dict

class QueueNames(JSON_parsable_Dict):
    FEATURE_TO_ADD = "feature_to_add"
    FEATURE_TO_REQUEST = "feature_to_request"
    DB_TO_ADD = "db_to_add"
    DB_TO_REQUEST = "db_to_request"
