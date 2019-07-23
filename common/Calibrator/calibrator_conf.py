import logging
from collections import namedtuple

from carlhauser_server.Configuration.algo_conf import Algo_conf
from common.environment_variable import JSON_parsable_Dict
from common.environment_variable import load_server_logging_conf_file
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf

load_server_logging_conf_file()


class Pair_rate_threshold:
    def __init__(self, rate, threshold):
        self.rate = rate
        self.threshold = threshold


class Default_calibrator_conf(JSON_parsable_Dict):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Calibrator inputs
        self.Acceptable_false_positive_rate: float = None
        self.Acceptable_false_negative_rate: float = None
        self.Minimum_true_positive_rate: float = None
        self.Minimum_true_negative_rate: float = None

        # Calibrator outputs
        self.thre_upper_at_least_xpercent_TPR: float = None
        self.thre_upper_at_most_xpercent_FNR: float = None
        self.thre_below_at_least_xpercent_TNR: float = None
        self.thre_below_at_most_xpercent_FPR: float = None
        self.maximum_F1: float = None

        # ==== Calibrator parameters # No obvious need to change them ====
        # Nb of points in the [0-1] interval that will be evaluated
        self.PTS_NB: int = 50
        # Minimum threshold where the evaluation will take place. If higher tha 0, no threshold could have a lesser threshold. NOT A GOOD WAY TO ENFORCE IT ;)
        self.MIN_THRESHOLD: float = 0
        # Maximum threshold where the evaluation will take place. If lower than 1, no threshold could have a higher threshold. NOT A GOOD WAY TO ENFORCE IT ;)
        self.MAX_THRESHOLD: float = 1
        # Number of first match to check to get the scores and overview. This means that the 3 first matches will be taken into account (distance only for now) to check for FP,TP ...
        self.NB_TO_CHECK: int = 3

    @staticmethod
    def get_default_instance():
        new_instance = Default_calibrator_conf()
        new_instance.Acceptable_false_positive_rate: float = 0.1
        new_instance.Acceptable_false_negative_rate: float = 0.1
        new_instance.Minimum_true_positive_rate: float = 0.9
        new_instance.Minimum_true_negative_rate: float = 0.9

    def validate(self):
        # Validate if at least two values are set and their values are acceptable

        case_1 = self.Minimum_true_negative_rate is not None and self.Acceptable_false_negative_rate is not None
        case_2 = self.Acceptable_false_positive_rate is not None and self.Acceptable_false_negative_rate is not None
        case_3 = self.Minimum_true_negative_rate is not None and self.Minimum_true_positive_rate is not None
        case_4 = self.Acceptable_false_positive_rate is not None and self.Minimum_true_positive_rate is not None

        if case_1:
            case_1_order = 0 <= self.Minimum_true_negative_rate <= self.Acceptable_false_negative_rate <= 1
            if not case_1_order:
                raise Exception("Invalid information to continue. Following formula not ensured : 0 <= (Minimum TNR) <= (Acceptable FNR) <= 1")
        elif case_2:
            case_2_order = 0 <= self.Acceptable_false_positive_rate <= self.Acceptable_false_negative_rate <= 1
            if not case_2_order:
                raise Exception("Invalid information to continue. Following formula not ensured : 0 <= (Acceptable FPR) <= (Acceptable FNR) <= 1 ")
        elif case_3:
            case_3_order = 0 <= self.Minimum_true_negative_rate <= self.Minimum_true_positive_rate <= 1
            if not case_3_order:
                raise Exception("Invalid information to continue. Following formula not ensured : 0 <= (Minimum TNR) <= (Minimum TPR) <= 1 ")
        elif case_4:
            case_4_order = 0 <= self.Acceptable_false_positive_rate <= self.Minimum_true_positive_rate <= 1
            if not case_4_order:
                raise Exception("Invalid information to continue. Following formula not ensured : 0 <= (Acceptable FPR) <= (Acceptable FNR) <= 1 ")
        else:
            raise Exception("Not enough information to continue. Please set :  (Acceptable FPR or Minimum TNR) AND (Acceptable FNR or Minimum TPR).")

        # All good. At least one pair is good.
        return True

    def return_good_pair(self):
        case_FNR_TNR = self.Minimum_true_negative_rate is not None and self.Acceptable_false_negative_rate is not None
        case_FNR_FPR = self.Acceptable_false_positive_rate is not None and self.Acceptable_false_negative_rate is not None
        case_TPR_TNR = self.Minimum_true_negative_rate is not None and self.Minimum_true_positive_rate is not None
        case_TPR_FPR = self.Acceptable_false_positive_rate is not None and self.Minimum_true_positive_rate is not None

        pair_FNR = Pair_rate_threshold(rate=self.Acceptable_false_negative_rate,
                                       threshold=self.thre_upper_at_most_xpercent_FNR)
        pair_TNR = Pair_rate_threshold(rate=self.Minimum_true_negative_rate,
                                       threshold=self.thre_below_at_least_xpercent_TNR)
        pair_FPR = Pair_rate_threshold(rate=self.Acceptable_false_positive_rate,
                                       threshold=self.thre_below_at_most_xpercent_FPR)
        pair_TPR = Pair_rate_threshold(rate=self.Minimum_true_positive_rate,
                                       threshold=self.thre_upper_at_least_xpercent_TPR)

        if case_FNR_TNR:
            return pair_TNR, pair_FNR
        elif case_FNR_FPR:
            return pair_FPR, pair_FNR
        elif case_TPR_TNR:
            return pair_TNR, pair_TPR
        elif case_TPR_FPR:
            return pair_FPR, pair_TPR
        else:
            raise Exception("Not enough information to continue. Please set :  (Acceptable FPR or Minimum TNR) AND (Acceptable FNR or Minimum TPR).")

    def export_to_Algo(self, input_Algo_Conf: Algo_conf) -> Algo_conf:
        # Overwrite parameter of the algorithm configuration
        # to apply the thresholds it contains to this algorithm configuration
        # AGGRESSIVE = Work on negative rate

        pair_1, pair_2 = self.return_good_pair()

        if pair_1.threshold > pair_2.threshold:
            self.logger.critical("Yes_to_Maybe threshold is upper than Maybe_to_no threshold : No MAYBE area !")

        input_Algo_Conf.threshold_yes_to_maybe = pair_1.threshold
        input_Algo_Conf.threshold_maybe_to_no = pair_2.threshold

        return input_Algo_Conf

    # ==================== To string ====================

    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' thre_upper_at_least_xpercent_TPR=', self.thre_upper_at_least_xpercent_TPR,
                                 ' thre_upper_at_most_xpercent_FNR=', self.thre_upper_at_most_xpercent_FNR,
                                 ' mean=', self.maximum_F1,
                                 ' thre_below_at_least_xpercent_TNR=', self.thre_below_at_least_xpercent_TNR,
                                 ' thre_below_at_most_xpercent_FPR=', self.thre_below_at_most_xpercent_FPR]))


def calibrator_conf_to_conf_file(cal_conf: Default_calibrator_conf) -> distance_engine_conf.Default_distance_engine_conf:
    basic_conf = distance_engine_conf.Default_distance_engine_conf()

    basic_conf.MAX_DIST_FOR_NEW_CLUSTER = cal_conf.maximum_F1

    return basic_conf


def parse_from_dict(conf):
    tmp_conf = Default_calibrator_conf()
    tmp_conf.__dict__.update(conf)
    # Or : tmp_conf.__dict__ = conf

    return tmp_conf
    # return namedtuple("Default_calibrator_conf", conf.keys())(*conf.values())
