#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import time
from typing import Dict

import requests

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from common.environment_variable import get_homedir, resolve_path, EndPoints


# ==================== ------ SERVER Flask API CALLER ------- ====================
class Simple_API:
    '''
    Provides "Low-level" API calls
    '''

    def __init__(self, url, certificate_path):
        self.server_url = url
        self.logger = logging.getLogger(__name__)
        self.cert = certificate_path

    @staticmethod
    def get_api():
        '''
        Static method that return an instance of the API (SimpleAPI type)
        :return: Simple API instance
        '''
        return Simple_API.get_custom_api(Simple_API)

    @staticmethod
    def get_custom_api(api_class):
        # Generate the API access point link to the hardcoded server
        cert = (get_homedir() / "carlhauser_client" / "cert.pem").resolve()

        # See : https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror
        # To create : openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
        api = api_class(url='https://localhost:5000/', certificate_path=cert)  # TODO : Should be =cert
        logging.captureWarnings(True)  # TODO : Remove
        return api

    # ================= UTILITIES =================
    def utility_extract_and_log_response(self, r: requests.Response) -> Dict:
        '''
        Extract the json version of the provided response (r), log it and return the data
        :param r: response of server
        :return: json format of the response
        '''
        data = r.json()  # Check the JSON Response Content documentation below
        self.logger.info("Response data : ", data)
        self.logger.info("Response content : ", r.content)
        return data

    def utility_image_to_HTTP_payload(self, file_path: pathlib.Path, img) -> Dict:
        # Construct the files attribute of the put request
        files = {'image': (file_path.name, img, 'multipart/form-data', {'Expires': '0'})}
        self.logger.debug(f"Ready to send picture in client : {type(img)} {img}")
        return files

    def utility_request_id_to_HTTP_payload(self, request_id: str) -> Dict:
        # Construct the files attribute of the put request
        # Construct the HTTP payload of the get request
        payload = {'request_id': request_id}
        return payload

    # ================= PING =================
    def ping_server(self) -> bool:
        '''
        Ping the server to check if he is alive with both GET and POST requests.
        :return: True if the server is alive (for GET and POST), False if the server is not
        '''
        r_get = self.ping_server_GET()
        data_get = self.utility_extract_and_log_response(r_get)

        r_post = self.ping_server_POST()
        data_post = self.utility_extract_and_log_response(r_post)

        return data_get["Called_function"] == "ping" and data_post["Called_function"] == "ping"

    def ping_server_GET(self) -> requests.Response:
        '''
        Ping the server to check if he is alive with GET request
        :return: the response from the server
        '''
        r = requests.get(url=self.server_url, verify=self.cert)
        self.logger.info(f"GET request => {r.status_code} {r.reason} {r.text}")
        return r

    def ping_server_POST(self) -> requests.Response:
        '''
        Ping the server to check if he is alive with POST request
        :return: the response from the server
        '''
        r = requests.post(url=self.server_url, verify=self.cert)
        self.logger.info(f"POST request => {r.status_code} {r.reason} {r.text}")
        return r

    # ================= ADD PICTURES =================

    def add_picture_server(self, file_path: pathlib.Path) -> (bool, str):
        '''
        Add one picture to the server
        :param file_path: the path of the picture to add
        :return: success or failure boolean, and the id of the added picture
        '''

        file_path = resolve_path(file_path)

        # Set the endpoint
        target_url = self.server_url + EndPoints.ADD_PICTURE

        # Send the picture
        # rb = Open a file for reading only in binary format. Starts reading from beginning of file.
        with open(str(file_path), 'rb') as img:
            # Construct the files attribute of the put request
            files = self.utility_image_to_HTTP_payload(file_path, img)

            # Create a session to send the "big file"
            with requests.Session() as s:
                # Execute the put request
                r = s.put(url=target_url, files=files, verify=self.cert)
                self.logger.info(f"PUT picture => {r.status_code} {r.reason} {r.text}")

                # Check the JSON Response Content documentation below
                data = self.utility_extract_and_log_response(r)

                return data["Status"] == "Success", data["img_id"]

    # ================= ADD PICTURES - WAITING =================

    # ================= REQUEST PICTURES =================

    def request_similar(self, file_path: pathlib.Path) -> (bool, str):
        '''
        Request similar picture of one picture to the server
        :param file_path: the path of the picture to request
        :return: success or failure boolean, and the id of the request picture
        '''

        file_path = resolve_path(file_path)

        # Set the endpoint
        target_url = self.server_url + EndPoints.REQUEST_PICTURE

        # Send the picture
        # rb = Open a file for reading only in binary format. Starts reading from beginning of file.
        with open(str(file_path), 'rb') as img:
            # Construct the files attribute of the put request
            files = self.utility_image_to_HTTP_payload(file_path, img)

            with requests.Session() as s:
                r = s.post(url=target_url, files=files, verify=self.cert)
                self.logger.info(f"POST picture request => {r.status_code} {r.reason} {r.text}")

                # Check the JSON Response Content documentation below
                data = self.utility_extract_and_log_response(r)

                return data["Status"] == "Success", data["request_id"]

    def get_results(self, request_id: str) -> (bool, Dict):
        '''
        Fetch the results of a request previously sent.
        :param request_id: the previously made request id
        :return: the answer of the server. #TODO : Give an example of answer
        '''

        # Set the endpoint
        target_url = self.server_url + EndPoints.GET_REQUEST_RESULT

        # Construct the HTTP payload of the request
        payload = self.utility_request_id_to_HTTP_payload(request_id)

        with requests.Session() as s:
            r = s.get(url=target_url, params=payload, verify=self.cert)
            self.logger.info(f"GET request results => {r.status_code} {r.reason} {r.text}")
            self.logger.info(r.content)

            data = r.json()  # Check the JSON Response Content documentation below
            self.logger.info(data)

            return data["Status"] == "Success", data["results"]

    # ================= REQUEST PICTURES - WAITING =================

    def poll_until_result_ready(self, request_id: str, max_time: int = -1) -> bool:
        '''
        Regularly ask the server if the results of the provided (request_id) are ready.
        Returns when ready or when timeout
        :param request_id: request_id response to wait for
        :param max_time: maximum allowed time to wait before timing out. By default -1 = No time out
        :return: boolean, True if request is ready, False if not
        '''

        # Starting count-down
        start_time = time.time()
        self.logger.info(f"Checking if {request_id} is ready. Start polling ...")

        # While the answer is not ready or we haven't timed-out
        time_out = False
        while not self.is_result_ready(request_id)[1] and not time_out:
            # Not ready yet, wait a bit
            self.logger.info(f"{request_id} not ready yet, waiting ...")
            time.sleep(2)

            # Compute if we are already in time out
            time_out = (abs(time.time() - start_time) > max_time and max_time != -1)

            if time_out:
                self.logger.info(f"{request_id} has still no answer. Time out ! ...")
                return False

        # Ready !
        self.logger.info(f"{request_id} got an answer.")
        return True

    def is_result_ready(self, request_id) -> (bool, bool):
        '''
        Ask the server if the results of the provided (request_id) is ready.
        :param request_id: request_id response to ask for
        :return: 2 booleans. First : True if the server answered, False otherwise. Second : True if the request is ready, False otherwise
        '''
        # Set the endpoint
        target_url = self.server_url + EndPoints.WAIT_FOR_REQUEST

        # Construct the HTTP payload of the request
        payload = self.utility_request_id_to_HTTP_payload(request_id)

        with requests.Session() as s:
            r = s.get(url=target_url, params=payload, verify=self.cert)
            self.logger.info(f"GET request is_ready => {r.status_code} {r.reason} {r.text}")

            # Check the JSON Response Content documentation below
            data = self.utility_extract_and_log_response(r)

            return data["Status"] == "Success", data["is_ready"]

    # ================= EXPORT AND DUMP =================

    def export_db_server(self) -> (bool, Dict):
        '''
        Ask the server a copy of the database
        :return: Boolean (True if server answered) and copy of the DB
        '''
        # Set the endpoint
        target_url = self.server_url + EndPoints.REQUEST_DB

        with requests.Session() as s:
            r = s.get(url=target_url, verify=self.cert)
            self.logger.info(f"GET request results => {r.status_code} {r.reason} {r.text}")

            # Check the JSON Response Content documentation below
            data = self.utility_extract_and_log_response(r)

            return data["Status"] == "Success", data["db"]
