#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

import requests

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


# ==================== ------ SERVER Flask API CALLER ------- ====================
class API_caller():
    def __init__(self, url, certificate_path):
        self.server_url = url
        self.logger = logging.getLogger(__name__)
        self.cert = certificate_path

    def ping_server(self):
        r = requests.get(url=self.server_url, verify=self.cert)
        self.logger.info(f"GET request => {r.status_code} {r.reason} {r.text}")

        r = requests.post(url=self.server_url, verify=self.cert)
        self.logger.info(f"POST request => {r.status_code} {r.reason} {r.text}")

        data = r.json()  # Check the JSON Response Content documentation below
        self.logger.info(data)

        return data["Called_function"] == "ping"

    def add_picture_server(self, file_path: pathlib.Path):
        # Solve the file path
        if not file_path.is_absolute():
            file_path = file_path.resolve()

        # Select the endpoint
        target_url = self.server_url + "add_picture"

        # Send the picture
        # rb = Open a file for reading only in binary format. Starts reading from beginning of file.
        with open(str(file_path), 'rb') as img:
            files = {'image': (file_path.name, img, 'multipart/form-data', {'Expires': '0'})}
            self.logger.debug(f"Image in client : {type(img)} {img}")
            with requests.Session() as s:
                r = s.put(url=target_url, files=files, verify=self.cert)
                self.logger.info(f"POST picture => {r.status_code} {r.reason} {r.text}")
                data = r.json()  # Check the JSON Response Content documentation below
                self.logger.info(r.content)
                self.logger.info(data)
                return data["Status"] == "Success", data["img_id"]
        # print(r.status_code, r.reason, r.text)

    def request_picture_server(self, file_path: pathlib.Path):
        # Solve the file path
        if not file_path.is_absolute():
            file_path = file_path.resolve()

        # Select the endpoint
        target_url = self.server_url + "request_similar_picture"

        # Send the picture
        # rb = Open a file for reading only in binary format. Starts reading from beginning of file.
        with open(str(file_path), 'rb') as img:
            files = {'image': (file_path.name, img, 'multipart/form-data', {'Expires': '0'})}
            self.logger.debug(f"Image in client : {type(img)} {img}")
            with requests.Session() as s:
                r = s.post(url=target_url, files=files, verify=self.cert)
                self.logger.info(f"POST picture request => {r.status_code} {r.reason} {r.text}")
                self.logger.info(r.content)

                data = r.json()  # Check the JSON Response Content documentation below
                self.logger.info(data)

                return data["Status"] == "Success", data["request_id"]


    def retrieve_request_results(self, request_id):
        # Select the endpoint
        target_url = self.server_url + "get_results"

        # Send the request_id
        payload = {'request_id': request_id}
        with requests.Session() as s:
            r = s.get(url=target_url, params=payload, verify=self.cert)
            self.logger.info(f"GET request results => {r.status_code} {r.reason} {r.text}")
            self.logger.info(r.content)

            data = r.json()  # Check the JSON Response Content documentation below
            self.logger.info(data)

            return data["Status"] == "Success", data["results"]

    def export_db_server(self):
        # Select the endpoint
        target_url = self.server_url + "export_db"

        # Send the request_id
        with requests.Session() as s:
            r = s.get(url=target_url, verify=self.cert)
            self.logger.info(f"GET request results => {r.status_code} {r.reason} {r.text}")
            self.logger.info(r.content)

            data = r.json()  # Check the JSON Response Content documentation below
            self.logger.info(data)

            return data["Status"] == "Success", data["db"]