# -*- coding: utf-8 -*-

import logging
import unittest

import common.Calibrator.calibrator_conf as calibrator_conf
import common.Calibrator.threshold_calibrator as threshold_calibrator
import common.PerformanceDatastructs.perf_datastruct as perf_datastruct
import common.PerformanceDatastructs.stats_datastruct as stats_datastruct
from common.ChartMaker.two_dimensions_plot import TwoDimensionsPlot
from common.environment_variable import get_homedir


# ASCII Art made with http://asciiflow.com/

class TestPerformanceEvaluator(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()
        self.output_folder = get_homedir() / "common_tests" / "Calibrator" / "Calibrator_conf_test"
        self.quality_evaluator = threshold_calibrator.Calibrator()
        self.plotmaker = TwoDimensionsPlot()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    '''
              Visualisation of goal
     +-------------------------------------+
     |                                TPR  |
     |                              XXXXXXXX
     |                           XXXX      |
     |                         XXX         |
     |                      XXXX           |
     |                  XXXXX              |
     |                XXX                  |
     |             XXXX                    |
     |          XXXX                       |
     |       XXXX                          |
     |     XXX                             |
     | XXXXX                               |
     |XX  FPR                              |
     +-------------------------------------+
     
    '''

    def get_increasing_graph(self):
        perf_list = []

        MAX_VAL = 20
        for i in range(0, MAX_VAL):
            t = i / MAX_VAL
            tmp_score = stats_datastruct.Stats_datastruct()
            tmp_score.TPR = (i / MAX_VAL)
            perf_list.append(perf_datastruct.Perf(score=tmp_score, threshold=t))

        return perf_list

    '''
                 Visualisation of goal
        +-------------------------------------+
        |X   TNR                              |
        | XXX                                 X
        |   XXX                               |
        |     XXX                             |
        |       XXX                           |
        |         XXX                         |
        |           XXX                       |
        |             XXXX                    |
        |                XXXX                 |
        |                   XXXXX             |
        |                       XXXXXX        |
        |                            XXXXXXX  |
        |                             FNR  XXX|
        +-------------------------------------+
    
    '''

    def get_decreasing_graph(self):
        perf_list = []

        MAX_VAL = 20
        for i in range(0, MAX_VAL):
            t = i / MAX_VAL
            tmp_score = stats_datastruct.Stats_datastruct()
            tmp_score.TPR = 1 - (i / MAX_VAL)
            perf_list.append(perf_datastruct.Perf(score=tmp_score, threshold=t))

        return perf_list

    '''
            Visualisation of goal
    +-------------------------------------+
    |X   TNR                         TPR  |
    | XXX                          XXXXXXXX
    |   XXX                     XXXX      |
    |     XXX                 XXX         |
    |       XXX            XXXX           |
    |         XXX      XXXXX              |
    |           XXX  XXX                  |
    |             XXXX                    |
    |          XXXX  XXXX                 |
    |       XXXX        XXXXX             |
    |     XXX               XXXXXX        |
    | XXXXX                      XXXXXXX  |
    |XX  FPR                      FNR  XXX|
    +-------------------------------------+
    '''

    def get_real_graph(self):
        perf_list = []

        MAX_VAL = 20
        last_F1 = 0
        for i in range(0, MAX_VAL):
            t = i / MAX_VAL
            tmp_score = stats_datastruct.Stats_datastruct()

            delta = 0.05
            tmp_score.TPR = (i / MAX_VAL)  # Increasing
            tmp_score.FPR = (i / MAX_VAL) + delta  # Increasing
            tmp_score.TNR = 1 - (i / MAX_VAL)  # Decreasing
            tmp_score.FNR = 1 - (i / MAX_VAL) - delta  # Decreasing
            if i < MAX_VAL / 2:
                tmp_score.F1 = (i / MAX_VAL)  # Increasing until some point
                last_F1 = tmp_score.F1
            else:
                tmp_score.F1 = last_F1

            perf_list.append(perf_datastruct.Perf(score=tmp_score, threshold=t))

        return perf_list

    '''
         +--------------------------+
         |X       way of iteration  |
         |  X       +------->       |
         |    X                     |
         |      X                   |
         |        X                 |
         |          X               |
         |            X             |
         |              X           |
returned |                X         |
value    +---------+--------X-------+
         |         ^         ^X     |
         |tolerance|         |  X   |
         |         |         |    X |
         +---------+---------+------+
         0                  0.9     1
                Returned threshold
    '''

    def test_get_min_threshold_for_max_attr_with_tolerance(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])

        thre, val = self.quality_evaluator.get_min_threshold_for_max_attr_with_tolerance(perfs_list=perf_list,
                                                                                         attribute="TPR",
                                                                                         tolerance=0.1)
        self.assertAlmostEqual(thre, 0.9, delta=0.1)

    '''
          +--------------------------+
 returned |X       way of iteration  |
 value    |  X       +------->       |
          | ^  X                     |
          | |    X                   |
          | |      X                 |
          | |        X               |
          | |          X             |
          | |            X           |
          | |              X         |
          | |                X       |
          | |                  X     |
          | |                    X   |
          | |                      X |
          +--------------------------+
          0                          1
           Returned threshold
    '''

    def test_get_max_threshold_for_max_attr(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])

        thre, val = self.quality_evaluator.get_max_threshold_for_max_attr(perfs_list=perf_list,
                                                                          attribute="TPR")
        self.assertAlmostEqual(thre, 0, delta=0.1)

    '''
            +--------------------------+
   returned |X       way of iteration  |
   value    |  X       +------->       |
            |    X                     |
            |      X                   |
            |        X                 |
            |          X               |
            |            X             |
            |              X           |
            |                X         |
            |                  X       |
            |                    X     |
            |                      X   |
            |                     ^  X |
            +---------------------+----+
            0                        1
                                Returned threshold
    '''

    def test_get_min_threshold_for_min_attr(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])

        thre, val = self.quality_evaluator.get_min_threshold_for_min_attr(perfs_list=perf_list,
                                                                          attribute="TPR")
        self.assertAlmostEqual(thre, 1, delta=0.1)

    '''
               Visualisation of goal
          +-------------------------------------+
          |                                TPR  |
          |                              XXXXXXXX
          |                           XXXX      |
          |                         XXX       ^ |
          |                      XXXX         | |
          |                  XXXXX            | |
          |                XXX                | |
          |             XXXX                  | |
          |          XXXX                     | |
          |       XXXX                        | |
          |     XXX                           | |
          | XXXXX                             | |
          |XX  FPR                            | |
          +-----------------------------------+-+
          Maximizing value of an increasing graph, while maximizing threshold
                    
          1 = leftmost higher (decreasing) = righmost higher (increasing)
    '''

    def test_get_max_max_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",  # Because generated graph has only TPR filled.
                                                                               higher=True,
                                                                               rightmost=True,
                                                                               is_increasing=True)
        self.logger.info(f"Found value {thre}")

        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="max_max_inc.png")
        self.assertAlmostEqual(thre, 1.0, delta=0.1)

    '''
                Visualisation of goal
           +-------------------------------------+
           |                                TPR  |
           |                              XXXXXXXX
           |                           XXXX      |
           |                         XXX    ^    |
           |                      XXXX      |    |
           |                  XXXXX         |    |
           |                XXX             |    |
           |             XXXX               |    |
           |          XXXX                  |    |
           |       XXXX                     |    |
           |     XXX                        |    |
           | XXXXX                          |    |
           |XX  FPR                         |    |
           +--------------------------------+----+
        Maximizing value of an increasing graph, while minimizing threshold
        
          2 = righmost higher (decreasing) = righmost lower (increasing)
    '''

    def test_get_max_min_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               higher=False,
                                                                               rightmost=True,
                                                                               is_increasing=True,
                                                                               tolerance=0.9)
        self.logger.info(f"Found value {thre}")
        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="max_min_inc.png")
        self.assertAlmostEqual(thre, 0.8, delta=0.1)

    '''
                   Visualisation of goal
          +-------------------------------------+
          |                                TPR  |
          |                              XXXXXXXX
          |                           XXXX      |
          |                         XXX         |
          |                      XXXX           |
          |                  XXXXX              |
          |                XXX                  |
          |             XXXX                    |
          |          XXXX                       |
          |       XXXX                          |
          |     XXX  ^                          |
          | XXXXX    |                          |
          |XX  FPR   |                          |
          +----------+--------------------------+
      Minimizing value of an increasing graph, while maximizing threshold
                
          3 = leftmost lower (decreasing) = leftmost higher (increasing)
    '''

    def test_get_min_max_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               higher=True,
                                                                               rightmost=False,
                                                                               is_increasing=True)
        self.logger.info(f"Found value {thre}")
        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="min_max_inc.png")
        self.assertAlmostEqual(thre, 0.2, delta=0.1)

    '''
                    Visualisation of goal
           +-------------------------------------+
           |                                TPR  |
           |                              XXXXXXXX
           |                           XXXX      |
           |                         XXX         |
           |                      XXXX           |
           |                  XXXXX              |
           |                XXX                  |
           |             XXXX                    |
           | +        XXXX                       |
           | |     XXXX                          |
           | v   XXX                             |
           | XXXXX                               |
           |XX  FPR                              |
           +-------------------------------------+
       Minimizing value of an increasing graph, while minimizing threshold
                 
        4 = rightmost lower (decreasing) = leftmost lower (increasing)
    '''

    def test_get_min_min_increasing(self):
        perf_list = self.get_increasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               higher=False,
                                                                               rightmost=False,
                                                                               is_increasing=True)
        self.logger.info(f"Found value {thre}")
        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="min_min_inc.png")
        self.assertAlmostEqual(thre, 0.0, delta=0.1)

    '''
                  Visualisation of goal
         +-------------------------------------+
         |X   TNR                              |
         | XXX                                 X
         |   XXX                               |
         | ^   XXX                             |
         | |     XXX                           |
         | |       XXX                         |
         | |         XXX                       |
         | |           XXXX                    |
         | |              XXXX                 |
         | |                 XXXXX             |
         | |                     XXXXXX        |
         | |                          XXXXXXX  |
         | |                           FNR  XXX|
         +-+-----------------------------------+
         Maximizing value of a decreasing graph, while Minimizing threshold
                   
          1 = leftmost higher (decreasing) = righmost higher (increasing)
     '''

    def test_get_max_max_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               higher=True,
                                                                               rightmost=False,
                                                                               is_increasing=False)
        self.logger.info(f"Found value {thre}")
        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="max_max_dec.png")
        self.assertAlmostEqual(thre, 0.0, delta=0.1)

    '''
              Visualisation of goal
         +-------------------------------------+
         |X   TNR                              |
         | XXX                                 X
         |   XXX                               |
         |     XXX                             |
         |       XXX                           |
         |     ^   XXX                         |
         |     |     XXX                       |
         |     |       XXXX                    |
         |     |          XXXX                 |
         |     |             XXXXX             |
         |     |                 XXXXXX        |
         |     |                      XXXXXXX  |
         |     |                       FNR  XXX|
         +-----+-------------------------------+
    Maximizing value of a decreasing graph, while Maximizing threshold
              
          2 = righmost higher (decreasing) = righmost lower (increasing)
    '''

    def test_get_max_min_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               higher=True,
                                                                               rightmost=True,
                                                                               is_increasing=False,
                                                                               tolerance=0.9)
        self.logger.info(f"Found value {thre}")
        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="max_min_dex.png")
        self.assertAlmostEqual(thre, 0.2, delta=0.1)

    '''
                 Visualisation of goal
        +-------------------------------------+
        |X   TNR                              |
        | XXX                                 X
        |   XXX                               |
        |     XXX                     +       |
        |       XXX                   |       |
        |         XXX                 |       |
        |           XXX               |       |
        |             XXXX            |       |
        |                XXXX         |       |
        |                   XXXXX     v       |
        |                       XXXXXX        |
        |                            XXXXXXX  |
        |                             FNR  XXX|
        +-------------------------------------+
    Minimum value of a decreasing graph, while minimizing threshold
              
    3 = leftmost lower (decreasing) = leftmost higher (increasing)
    '''

    def test_get_min_max_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               higher=False,
                                                                               rightmost=False,
                                                                               is_increasing=False)
        self.logger.info(f"Found value {thre}")
        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="min_max_dec.png")
        self.assertAlmostEqual(thre, 0.8, delta=0.1)

    '''
              Visualisation of goal
         +-------------------------------------+
         |X   TNR                              |
         | XXX                                 X
         |   XXX                               |
         |     XXX                             |
         |       XXX                           |
         |         XXX                         |
         |           XXX                     + |
         |             XXXX                  | |
         |                XXXX               | |
         |                   XXXXX           | |
         |                       XXXXXX      v |
         |                            XXXXXXX  |
         |                             FNR  XXX|
         +-------------------------------------+
    Minimum value of a decreasing graph, while maximizing threshold
              
    4 = rightmost lower (decreasing) = leftmost lower (increasing)
    '''

    def test_get_min_min_decreasing(self):
        perf_list = self.get_decreasing_graph()
        print([p.score.TPR for p in perf_list])
        thre, val = self.quality_evaluator.get_optimal_for_optimized_attribute(perfs_list=perf_list,
                                                                               attribute="TPR",
                                                                               higher=False,
                                                                               rightmost=True,
                                                                               is_increasing=False)
        self.logger.info(f"Found value {thre}")
        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre
        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="min_min_dec.png")
        self.assertAlmostEqual(thre, 1.0, delta=0.1)

    def test_real_graph(self):
        perf_list = self.get_real_graph()
        print([p.score.TPR for p in perf_list])
        print([p.score.TNR for p in perf_list])
        print([p.score.FPR for p in perf_list])
        print([p.score.FNR for p in perf_list])

        Minimum_true_positive_rate = 0.9
        Acceptable_false_negative_rate = 0.1
        Minimum_true_negative_rate = 0.9
        Acceptable_false_positive_rate = 0.1

        thre_max_TPR, val_TPR = self.quality_evaluator.get_threshold_where_upper_are_more_than_xpercent_TP(perfs_list=perf_list, percent=Minimum_true_positive_rate)
        thre_max_FNR, val_FNR = self.quality_evaluator.get_threshold_where_upper_are_less_than_xpercent_FN(perfs_list=perf_list, percent=Acceptable_false_negative_rate)
        thre_max_TNR, val_TNR = self.quality_evaluator.get_threshold_where_below_are_more_than_xpercent_TN(perfs_list=perf_list, percent=Minimum_true_negative_rate)
        thre_max_FPR, val_FPR = self.quality_evaluator.get_threshold_where_below_are_less_than_xpercent_FP(perfs_list=perf_list, percent=Acceptable_false_positive_rate)
        thre_max_F1, val_F1 = self.quality_evaluator.get_max_threshold_for_max_F1(perfs_list=perf_list)

        self.logger.info(f"Found value TPR : {thre_max_TPR} for {val_TPR} / upper there is more than 90% true positive")
        self.logger.info(f"Found value TNR : {thre_max_TNR} for {val_TNR} / below there is more than 90% true negative")
        self.logger.info(f"Found value FNR : {thre_max_FNR} for {val_FNR} / upper there is less than 10% false negative")
        self.logger.info(f"Found value FPR : {thre_max_FPR} for {val_FPR} / below there is less than 10% false positive")
        self.logger.info(f"Found value F1 :  {thre_max_F1} for {val_F1}")

        tmp_conf = calibrator_conf.Default_calibrator_conf()
        tmp_conf.thre_below_at_least_xpercent_TNR = thre_max_TNR
        tmp_conf.thre_upper_at_most_xpercent_FNR = thre_max_FNR
        tmp_conf.thre_upper_at_least_xpercent_TPR = thre_max_TPR
        tmp_conf.thre_below_at_most_xpercent_FPR = thre_max_FPR
        tmp_conf.maximum_F1 = thre_max_F1

        self.plotmaker.print_graph_with_thresholds(perf_list, thresholds_handler=tmp_conf,
                                                   output_path=self.output_folder,
                                                   file_name="real_graph.png")

        self.assertAlmostEqual(thre_max_TPR, 0.8, delta=0.1)
        self.assertAlmostEqual(thre_max_TNR, 0.2, delta=0.1)
        self.assertAlmostEqual(thre_max_FNR, 0.8, delta=0.1)
        self.assertAlmostEqual(thre_max_FPR, 0.1, delta=0.1)  # Would have been 0.2 without delta
        self.assertAlmostEqual(thre_max_F1, 0.5, delta=0.1)


if __name__ == '__main__':
    unittest.main()
