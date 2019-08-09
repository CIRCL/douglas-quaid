#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import traceback
from typing import Dict, List
import numpy as np

import cv2
import math

import carlhauser_server.Configuration.database_conf as database_conf
import carlhauser_server.Configuration.distance_engine_conf as distance_engine_conf
import carlhauser_server.Configuration.feature_extractor_conf as feature_extractor_conf
import carlhauser_server.DistanceEngine.scoring_datastrutures as sd
from carlhauser_server.Configuration.algo_conf import Algo_conf
from carlhauser_server.DistanceEngine.distance_hash import Distance_Hash as dist_hash
from common.CustomException import AlgoFeatureNotPresentError
from carlhauser_server.DistanceEngine.distance_orb import Distance_ORB


class Distance_RANSAC_ORB:
    def __init__(self, db_conf: database_conf.Default_database_conf, dist_conf: distance_engine_conf.Default_distance_engine_conf, fe_conf: feature_extractor_conf.Default_feature_extractor_conf):
        # STD attributes
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creation of a Distance ORB Engine")

        # Save configuration
        self.db_conf = db_conf  # TODO : REMOVE = NOT USEFUL FOR NOW !
        self.dist_conf = dist_conf
        self.fe_conf = fe_conf

        self.orb_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=dist_conf.CROSSCHECK)

    def ransac_orb_distance(self, pic_package_from: Dict, pic_package_to: Dict) -> Dict[str, sd.AlgoMatch]:
        """
        Distance between two provided pictures (dicts) with RANSAC-ORB methods
        :param pic_package_from: first picture dict
        :param pic_package_to: second picture dict
        :return: A dictionary of algo name to the match detail (distance, decision ..)
        """

        answer = {}
        self.logger.info("RANSAC-Orb distance computation ... ")

        # Verify if what is needed to compute it is present
        if pic_package_from.get("ORB_DESCRIPTORS", None) is None \
                or pic_package_to.get("ORB_DESCRIPTORS", None) is None:
            self.logger.warning(f"RANSAC-ORB descriptors are NOT presents in the results.")
            raise AlgoFeatureNotPresentError("None RANSAC-ORB descriptors in orb distance.")

        # Verify if what is needed to compute it is present
        if pic_package_from.get("ORB_KEYPOINTS", None) is None \
                or pic_package_to.get("ORB_KEYPOINTS", None) is None:
            self.logger.warning(f"RANSAC-ORB keypoints are NOT presents in the results.")
            raise AlgoFeatureNotPresentError("None RANSAC-ORB keypoints in orb distance.")

        # Add result for enabled algorithms
        try:
            if self.fe_conf.RANSAC_ORB.get("is_enabled", False):
                answer = self.add_results(self.fe_conf.RANSAC_ORB, pic_package_from, pic_package_to, answer)

        except Exception as e:
            self.logger.error(traceback.print_tb(e.__traceback__))
            self.logger.error("Error during RANSAC-orb distance calculation : " + str(e))

        return answer

    def add_results(self, algo_conf: Algo_conf, pic_package_from: Dict, pic_package_to: Dict, answer: Dict) -> Dict:
        """
        Add results to answer dict, depending on the algorithm name we want to compute
        Ex : Input {} -> Output {"RANSAC_ORB":{"name":"RANSAC_ORB", "distance":0.3,"decision":YES}}
        :param algo_conf: An algorithm configuration (to specify which algorithm to launch)
        :param pic_package_from: first picture dict
        :param pic_package_to: second picture dict
        :param answer: Current dict of algo_name to algo match (will be updated and returned)
        :return: a dict of algo_name to algo match
        """

        algo_name = algo_conf.get('algo_name')

        tmp_dist = self.compute_ransac_distance(pic_package_from, pic_package_to)

        # Add the distance as an AlgoMatch
        answer[algo_name] = sd.AlgoMatch(name=algo_name,
                                         distance=tmp_dist,
                                         decision=self.compute_decision_from_distance(algo_conf, tmp_dist))

        return answer

    def compute_ransac_distance(self, pic_package_from: Dict, pic_package_to: Dict, ) -> float:
        """
        Compute distance with RANSAC from two set of descriptors
        :param pic_package_to:
        :param pic_package_from:
        :return: distance between descriptors
        """

        descriptors_1 = pic_package_from["ORB_DESCRIPTORS"]
        keypoints_1 = pic_package_from["ORB_KEYPOINTS"]  # TODO : To verify if good name
        descriptors_2 = pic_package_to["ORB_DESCRIPTORS"]
        keypoints_2 = pic_package_to["ORB_KEYPOINTS"]  # TODO : To verify if good name

        if descriptors_1 is None and descriptors_2 is None:
            # Both pictures don't have descriptors : the same !
            return 0
        elif descriptors_1 is None or descriptors_2 is None:
            # Only one picture does not have any descriptor. Not the same at all !
            return 1

        # Extract matches from ORB matcher
        matches = self.orb_matcher.match(descriptors_1, descriptors_2)
        self.logger.debug(f"matches : {matches}")

        # Filter matches with method chosen
        reduced_matches = self.filter_matches(matches, self.dist_conf.MATCHES_THRESHOLD_TO_ACCELERATE)
        if len(reduced_matches) > self.dist_conf.MIN_NB_MATCHES_TO_FIND_HOMOGRAPHY:
            good, transformation_matrix, transformation_rigid_matrix = self.find_homography(keypoints_1, keypoints_2, reduced_matches)
        else:
            self.logger.info(f"RANSAC Computation : Not enough matches between both pictures to continue.")
            return 1

        # Compute distance out of kepts matches
        # TODO :
        self.filter_matrix_all(transformation_matrix)
        self.filter_matrix_all(transformation_rigid_matrix)

        if len(matches) == 0:
            return 1
            # raise Exception(f"No match for these descriptors list : {descriptors_1} {descriptors_2}")
        else:
            return Distance_ORB.max_dist(matches, Distance_ORB.threeshold_distance_filter(matches))

    @staticmethod
    def filter_matches(matches: List, matches_threshold_to_accelerate: float) -> List:
        # Output a list of filtered matches, according to distance
        # Do remove the farthest matches to greatly accelerate RANSAC
        # From : http://answers.opencv.org/question/984/performance-of-findhomography/

        diminished_matches = []
        for m in matches:
            if m.distance < matches_threshold_to_accelerate:
                diminished_matches.append(m)

        return diminished_matches

    @staticmethod
    def find_homography(keypoints_pic1, keypoints_pic2, matches) -> (List, np.float32, np.float32):
        # Find an Homography matrix between two pictures
        # From two list of keypoints and a list of matches, extrat
        # A list of good matches found by RANSAC and two transformation matrix (an homography and a rigid homography/affine)

        # Instanciate outputs
        good = []

        # Transforming keypoints to list of points
        src_pts = np.float32([keypoints_pic1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints_pic2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        # Find the transformation between points
        transformation_matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Compute a rigid transformation (without depth, only scale + rotation + translation)
        transformation_rigid_matrix, rigid_mask = cv2.estimateAffinePartial2D(src_pts, dst_pts)

        # Get a mask list for matches = A list that says "This match is an in/out-lier"
        matchesMask = mask.ravel().tolist()

        # Filter the matches list thanks to the mask
        for i, element in enumerate(matchesMask):
            if element == 1:
                good.append(matches[i])

        return good, transformation_matrix, transformation_rigid_matrix

    def filter_matrix_all(self, matrix) -> float:
        # Ideas from :
        # - https://stackoverflow.com/questions/10972438/detecting-garbage-homographies-from-findhomography-in-opencv/10981249#10981249
        # - https://stackoverflow.com/questions/14954220/how-to-check-if-obtained-homography-matrix-is-good?noredirect=1&lq=1
        # - https://stackoverflow.com/questions/16439792/how-can-i-compute-svd-and-and-verify-that-the-ratio-of-the-first-to-last-singula?noredirect=1&lq=1
        # - https://answers.opencv.org/question/2588/check-if-homography-is-good/

        list_dist = []

        self.logger.debug(f"Compute Matrix determinant ...")
        det = self.compute_matrix_det(matrix)

        self.logger.debug(f"Comment Matrix determinant ...")
        self.comment_matrix_det(det)

        self.logger.debug(f"Analyse Matrix determinant ...")
        dist_zero = self.filter_zero_det(det)
        dist_orient = self.filter_det_orientation(det)

        self.logger.debug(f"Analyse Matrix SVD ...")
        # TODO : dist_svd = self.filter_matrix_svd(matrix)

        self.logger.debug(f"Analyse Image corners ...")
        pts, max = self.compute_matrix_pictures_corners()

        self.logger.debug(f"Distances measured :")
        self.logger.debug(f"Zero determinant distance : {dist_zero}")
        self.logger.debug(f"Orientation distance : {dist_orient} ")
        # TODO : self.logger.debug(f"SVD distance : {dist_svd} ")
        list_dist.append(dist_zero)
        list_dist.append(dist_orient)
        # TODO : list_dist.append(dist_svd)

        try:
            self.logger.debug(f"-> With Homography transformation...")
            dist_homo, transformed_pts_homo = self.filter_matrix_corners_homography(pts, max, matrix)
            if transformed_pts_homo is not None:
                dist_order_homo = self.filter_corners_direction(transformed_pts_homo)

                self.logger.debug(f"Homography distance : {dist_homo} ")
                self.logger.debug(f"Order from homography distance : {dist_order_homo} ")
                list_dist.append(dist_homo)
                list_dist.append(dist_order_homo)

        except Exception as e:
            self.logger.error(f"Inverting RANSAC transformation matrix impossible due to : {e}")

        try:
            self.logger.debug(f"-> With Affine transformation ...")
            dist_affine, transformed_pts_affine = self.filter_matrix_corners_affine(pts, max, matrix)
            if transformed_pts_affine is not None:
                dist_order_affine = self.filter_corners_direction(transformed_pts_affine)

                self.logger.debug(f"Affine distance : {dist_affine} ")
                self.logger.debug(f"Order from homography distance : {dist_order_affine} ")
                list_dist.append(dist_affine)
                list_dist.append(dist_order_affine)

        except Exception as e:
            self.logger.error(f"Inverting RANSAC transformation matrix impossible due to : {e}")

        # Mean all values found
        if 1 in list_dist or len(list_dist) == 0:
            return 1
        else:
            return sum(list_dist) / len(list_dist)

    @staticmethod
    def compute_matrix_det(matrix):
        '''
        Compute the determinant of the homography, and see if it's too close to zero for comfort.
        Compute the determinant of the top left 2x2 homography matrix, and check if it's "too close" to zero for comfort...
        btw you can also check if it's *too *far from zero because then the invert matrix would have a determinant too close to zero.
        '''
        det = matrix[0][0] * matrix[0][0] - matrix[1][0] * matrix[0][1]
        return det

    def comment_matrix_det(self, det):
        if det == 1:
            self.logger.debug(f"Almost 90° rotation for current comparison.")
        elif det < 0:
            self.logger.debug(f"Mirror scene for for current comparison.")

    @staticmethod
    def filter_zero_det(det):
        '''
        A determinant of zero would mean the matrix is not inversible, too close to zero would mean *singular
        (like you see the plane object at 90°, which is almost impossible if you use *good matches).
        '''
        threshold = 1
        if math.fabs(det) > threshold:  # or math.fabs(det) < (1.0 / threshold) :
            return 1  # bad

    @staticmethod
    def filter_det_orientation(det):
        '''
        And while we are at it...if det<0 the homography is not conserving the orientation (clockwise<->anticlockwise), 
        except if you are watching the object in a mirror...it is certainly not good (plus the sift/surf descriptors are not done to be mirror invariants as far as i know, so you would probably don'thave good maches).
        Else if the determinant is < 0, it is orientation-reversing.
        '''
        # H.at < double > (0, 0) * H.at < double > (1, 1) - H.at < double > (1, 0) * H.at < double > (0, 1);
        if det < 0:
            return 1  # no mirrors in the scene

    @staticmethod
    def filter_matrix_svd(matrix):
        '''
        Even better, compute its SVD, and verify that the ratio of the first-to-last singular value is sane (not too high).
        Either result will tell you whether the matrix is close to singular.
        you'd have to verify that the largest eigen-value isn't too small too.
        '''
        # TODO
        pass

    @staticmethod
    def compute_matrix_pictures_corners():
        # Get the size of the current matching picture
        # TODO : Store somewhere the shape of the uploaded picture ?
        # h, w, d = pic1.image.shape
        # TODO : For now, just take a random size picture
        h, w, d = 1000, 1000, 3

        # Get the position of the 4 corners of the current matching picture
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        max = 4 * cv2.norm(np.float32([[w, h]]), cv2.NORM_L2)

        return pts, max

    @staticmethod
    def filter_matrix_corners_homography(pts, max, matrix) -> (float, List):
        '''
        Compute the images of the image corners and of its center (i.e. the points you get when you apply the homography to those corners and center),
        and verify that they make sense, i.e. are they inside the image canvas (if you expect them to be)? Are they well separated from each other?
        Return a distance and a list of the transformed points
        '''

        # Transform the 4 corners thanks to the transformation matrix calculated
        transformed_pts = cv2.perspectiveTransform(pts, matrix)

        # Compute the difference between original and modified position of points
        dist = round(cv2.norm(pts - transformed_pts, cv2.NORM_L2) / max, 10)  # sqrt((X1-X2)²+(Y1-Y2)²+...)

        # Totally an heuristic (geometry based):
        if dist < 0.20:
            return dist, transformed_pts
        else:
            return 1, transformed_pts

    @staticmethod
    def filter_matrix_corners_affine(pts, max, matrix) -> (float, List):
        '''
        Compute the images of the image corners and of its center (i.e. the points you get when you apply the homography to those corners and center),
        and verify that they make sense, i.e. are they inside the image canvas (if you expect them to be)? Are they well separated from each other?
        Return a distance and a list of the transformed points
        '''

        # Make affine transformation
        add_row = np.array([[0, 0, 1]])
        affine_matrix = np.concatenate((matrix, add_row), axis=0)
        transformed_pts_affine = cv2.perspectiveTransform(pts, affine_matrix)

        # Affine distance
        tmp_dist_affine = round(cv2.norm(pts - transformed_pts_affine, cv2.NORM_L2) / max, 10)  # sqrt((X1-X2)²+(Y1-Y2)²+...)

        # Totally an heuristic (geometry based):
        if tmp_dist_affine < 0.20:
            return tmp_dist_affine, transformed_pts_affine
        else:
            return 1, transformed_pts_affine

    @staticmethod
    def filter_corners_direction(transformed_pts):
        '''
        Homography should preserve the direction of polygonal points.
        Design a simple test. points (0,0), (imwidth,0), (width,height), (0,height) represent a quadrilateral with clockwise arranged points.
        Apply homography on those points and see if they are still clockwise arranged if they become counter clockwise your homography is flipping (mirroring)
        the image which is sometimes still ok. But if your points are out of order than you have a "bad homography"
        '''
        # Direction of polygones : check if order is consistent
        corner_TL = transformed_pts[0][0]  # Top Left
        corner_TR = transformed_pts[3][0]  # Top Right
        corner_BL = transformed_pts[1][0]  # Bottom Left
        corner_BR = transformed_pts[2][0]  # Bottom Right

        # Test the order
        if not (corner_TL[0] < corner_TR[0] and corner_BL[0] < corner_BR[0] and corner_TL[1] < corner_BL[1] and corner_TR[1] < corner_BR[1]):
            return 1

    @staticmethod
    def filter_other_idea_1(self):
        '''
        Plot in matlab/octave the output (data) points you fitted the homography to, along with their computed values from the input ones,
        using the homography, and verify that they are close (i.e. the error is low).
        '''

    @staticmethod
    def filter_other_idea_2(self):
        '''
        The homography doesn't change the scale of the object too much. For example if you expect it to shrink or enlarge the image by a factor of up to X, just check this rule. Transform the 4 points (0,0), (imwidth,0), (width-1,height), (0,height) with homography and calculate the area of the quadrilateral (opencv method of calculating area of polygon) if the ratio of areas is too big (or too small), you probably have an error.
        '''

    @staticmethod
    def filter_other_idea_3(self):
        '''
        Good homography is usually uses low values of perspectivity.
        Typically if the size of the image is ~1000x1000 pixels those values should be ~0.005-0.001.
        High perspectivity will cause enormous distortions which are probably an error. If you don't know where those values are located read my post:
        trying to understand the Affine Transform . It explains the affine transform math and the other 2 values are perspective parameters.
        '''

    @staticmethod
    def filter_other_idea_4(self):
        '''
        Compute the area before/after
        '''

    # ==================== ------ DECISIONS ------- ====================

    @staticmethod
    def compute_decision_from_distance(algo_conf: Algo_conf, dist: float) -> sd.DecisionTypes:
        """
        From a distance between orb distance, gives a decision : is it a match or not ? Or maybe ?
        # TODO : Evolve to more complex calculation if needed for ORB !
        :param algo_conf: An algorithm configuration (to specify which algorithm to launch)
        :param dist: a distance between two pictures
        :return: a decision (YES,MAYBE,NO)
        """

        return dist_hash.compute_decision_from_distance(algo_conf, dist)
