#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import pathlib

from carlhauser_client.API.extended_api import Extended_API
from carlhauser_client.API.simple_api import Simple_API
from common.environment_variable import get_homedir
from common.environment_variable import load_client_logging_conf_file

load_client_logging_conf_file()


# ==================== ------ LAUNCHER ------- ====================
class ClientInstanceExample:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.API = Extended_API.get_api()

    def launch(self):
        """
        Small example of adding, requesting, polling, adding, fetching, dumping ...
        """

        self.logger.info(f"Launching webservice ...")
        self.perform_ping_check()
        self.perform_upload(get_homedir() / "datasets" / "simple_pictures" / "image.jpg")

        self.logger.info(f"Add ? ")
        input()
        self.perform_upload(get_homedir() / "datasets" / "simple_pictures" / "image.png")

        self.logger.info(f"Request ? ")
        input()
        request_id = self.perform_request(get_homedir() / "datasets" / "simple_pictures" / "image.bmp")

        self.logger.info(f"Polling ... ")
        self.poll_until_result_ready(request_id)

        self.logger.info(f"Add ? ")
        input()
        self.perform_upload(get_homedir() / "datasets" / "simple_pictures" / "image.bmp")

        self.logger.info(f"Fetch result ? ")
        input()
        self.retrieve_request_results(request_id)

        self.logger.info(f"Dump DB ? ")
        input()
        self.export_db_server()

    def perform_ping_check(self):
        self.API.ping_server()

    def perform_upload(self, path: pathlib.Path):
        self.API.add_one_picture(path)

    def perform_request(self, path: pathlib.Path):
        return self.API.request_similar(path)[1]

    def poll_until_result_ready(self, request_id):
        return self.API.poll_until_result_ready(request_id, max_time=60)

    def retrieve_request_results(self, request_id):
        return self.API.get_results(request_id)[1]

    def export_db_server(self):
        return self.API.export_db_server()[1]

    @staticmethod
    def example():
        # Generate the API access point link to the hardcoded server
        cert = (get_homedir() / "carlhauser_client" / "cert.pem").resolve()
        api = Simple_API(url='https://localhost:5000/', certificate_path=cert)

        # Ping server, and perform uploads
        api.ping_server()
        api.add_one_picture(get_homedir() / "datasets" / "simple_pictures" / "image.jpg")
        # (...)

        # Request a picture matches
        request_id = api.request_similar(get_homedir() / "datasets" / "simple_pictures" / "image.bmp")[1]
        # (...)

        # Wait a bit
        api.poll_until_result_ready(request_id, max_time=60)

        # Retrieve results of the previous request
        api.get_results(request_id)

        # Triggers a DB export of the server as-is, to be displayed with visjsclassificator. Dump to a file on server side too.
        graph = api.export_db_server()[1]

    @staticmethod
    def example_automated():
        # Generate the API access point link to the hardcoded server
        cert = (get_homedir() / "carlhauser_client" / "cert.pem").resolve()
        api = Extended_API(url='https://localhost:5000/', certificate_path=cert)

        # Ping server, and perform uploads
        api.ping_server()
        api.add_many_pictures_and_wait_global(get_homedir() / "datasets" / "simple_pictures")
        # (...)

        # Request a picture matches
        list_answers, nb_pics = api.request_many_pictures_and_wait_global(get_homedir() / "datasets" / "simple_pictures")
        # (...)

        # Triggers a DB export of the server as-is, to be displayed with visjsclassificator. Dump to a file on server side too.
        graph = api.export_db_server()[1]

    @staticmethod
    def example_full_automated():
        # Generate the API access point link to the hardcoded server
        api = Extended_API.get_api()

        # Ping server, and perform uploads
        api.ping_server()

        # Request a picture matches
        list_answers = api.add_and_request_and_dump_pictures(get_homedir() / "datasets" / "simple_pictures")

        # Triggers a DB export of the server as-is, to be displayed with visjsclassificator. Dump to a file on server side too.
        graph = api.export_db_server()[1]

    @staticmethod
    def example_minimal():
        # Generate the API access point link to the hardcoded server
        api = Extended_API.get_api()

        # Request a picture matches
        list_answers = api.add_and_request_and_dump_pictures(get_homedir() / "datasets" / "simple_pictures")


if __name__ == '__main__':
    client_instance = ClientInstanceExample()
    client_instance.launch()
