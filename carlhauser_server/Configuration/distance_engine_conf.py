from collections import namedtuple

from common.environment_variable import JSON_parsable_Dict

class Default_distance_engine_conf(JSON_parsable_Dict):
    def __init__(self):
        # Inputs
        self.TOP_N_CLUSTERS: int = 3  # Nb of "best clusters" to be matched on picture representative
        self.TOP_N_PICTURES: int = 10  # Nb of "best pictures" to be returned, from TOP_N_CLUSTERS best clusters (total, not per cluster)
        self.PICT_TO_TEST_PER_CLUSTER: int = 1  # Nb of "central picture" to test per cluster

        self.MAX_DIST_FOR_NEW_CLUSTER: float = 0.2  # Distance threshold to create a new cluster. Lesser the more cluster.

        # HASH PARAMETERS

        # ORB PARAMETERS
        self.CROSSCHECK: bool = True



def parse_from_dict(conf):
    tmp_conf = Default_distance_engine_conf()
    tmp_conf.__dict__.update(conf)
    # Or : tmp_conf.__dict__ = conf

    return tmp_conf
    # return namedtuple("Default_distance_engine_conf", conf.keys())(*conf.values())


'''
    self.GROUND_TRUTH_PATH = None
    self.IMG_TYPE = SUPPORTED_IMAGE_TYPE.PNG
    # Processing
    self.ALGO = ALGO_TYPE.A_HASH
    self.SELECTION_THREESHOLD = None #TODO : To fix and to use, to prevent "forced linked" if none
    # Threshold
    self.THREESHOLD_EVALUATION = THRESHOLD_MODE.MAXIMIZE_TRUE_POSITIVE
    # Output
    self.SAVE_PICTURE_INSTRUCTION_LIST = []
    self.OUTPUT_DIR = None
'''

'''
# ==================== To string ====================

# Overwrite to print the content of the cluster instead of the cluster memory address
def __repr__(self):
    return self.get_str()

def __str__(self):
    return self.get_str()

def get_str(self):
    return ''.join(map(str, [' \nTOP_N_CLUSTERS=', self.TOP_N_CLUSTERS,
                             ' \nTOP_N_PICTURES=', self.TOP_N_PICTURES,
                             ' \nPICT_TO_TEST_PER_CLUSTER=', self.PICT_TO_TEST_PER_CLUSTER,
                             ' \nMAX_DIST_FOR_NEW_CLUSTER=', self.MAX_DIST_FOR_NEW_CLUSTER,
                             ' \nCROSSCHECK=', self.CROSSCHECK]))

'''
