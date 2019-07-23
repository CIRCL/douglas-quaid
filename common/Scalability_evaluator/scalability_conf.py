import logging
from collections import namedtuple
from typing import List

from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.environment_variable import JSON_parsable_Dict
from common.environment_variable import load_server_logging_conf_file
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf

load_server_logging_conf_file()


class Default_scalability_conf(JSON_parsable_Dict):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.NB_PICS_TO_REQUEST = 10

        self.STARTING_NB_PICS_IN_DB = 5
        self.MULTIPLIER_LIST = [2, 5]

    def generate_boxes(self, max_nb_pictures: int) -> List[int]:
        """
        Generate a list of boxes size from a list of multiplier, a starting point and a maximum list of picture. From 10 000 and [2,5], and 5, generates [5,10,50,100,500, 1000 ...]
        :param max_nb_pictures: Maximum box size to reach
        :return: A List of integer
        """
        list_boxes = []
        max_boxes = 100  # Hard limit to generate boxes. No more than 100 points.
        curr_box = self.STARTING_NB_PICS_IN_DB

        i = 0
        box_reached_max = False

        while len(list_boxes) < max_boxes and not box_reached_max:
            # Multiply current box size per the current multiplier
            curr_box = self.MULTIPLIER_LIST[i] * curr_box

            list_boxes.append(curr_box)

            # If we went out of bound, stop
            if curr_box >= max_nb_pictures:
                box_reached_max = True

            # Get the next multiplier
            i = (i + 1) % len(self.MULTIPLIER_LIST)

        return list_boxes

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' thre_upper_at_least_xpercent_TPR=', self.thre_upper_at_least_xpercent_TPR,
                                 ' thre_upper_at_most_xpercent_FNR=', self.thre_upper_at_most_xpercent_FNR]))


def parse_from_dict(conf):
    return namedtuple("Default_calibrator_conf", conf.keys())(*conf.values())
