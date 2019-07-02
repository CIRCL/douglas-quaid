#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Not that this could use : flask/bin/python
# Inspired from : https://github.com/D4-project/IPASN-History/blob/master/website/web/__init__.py
# If you are derouted by the lack of decorator, go there : https://stackoverflow.com/questions/17129573/can-i-use-external-methods-as-route-decorators-in-python-flask

import argparse
import logging
import os
import pathlib
import sys
import time

# ==================== ------ STD LIBRARIES ------- ====================
import flask

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from common.environment_variable import get_homedir, dir_path

import carlhauser_server.Configuration.webservice_conf as webservice_conf
import carlhauser_server.Configuration.database_conf as database_conf

import carlhauser_server.Helpers.id_generator as id_generator
import common.ImportExport.picture_import_export as picture_import_export
import carlhauser_server.DatabaseAccessor.database_worker as database_worker

import common.ImportExport.json_import_export as json_import_export
import carlhauser_server.DatabaseAccessor.database_utilities as db_utils


# ==================== ------ SERVER Flask API definition ------- ====================

class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        # self.response = flask.Response("Welcome to carl-hauser", status=200, headers={})

    def __call__(self, *args):
        # Perform the action
        answer = self.action(*args)

        # Create the answer (bundle it in a correctly formatted HTTP answer)
        if isinstance(answer, str):
            # If it's a string, we bundle it has a HTML-like answer
            self.response = flask.Response(answer, status=200, headers={})
        else:
            # If it's something else (dict, ..) we jsonify and send it
            self.response = flask.jsonify(answer)

        # Send it
        return self.response


class FlaskAppWrapper(object):
    def __init__(self, name, ws_conf: webservice_conf, db_conf: database_conf):
        # STD attributes
        self.conf = ws_conf
        self.logger = logging.getLogger(__name__)

        # Specific attributes
        self.app = flask.Flask(name)
        # An accessor to push stuff in queues, mainly
        self.database_worker = database_worker.Database_Worker(db_conf=db_conf)
        self.db_utils = None

    def run(self):
        # Handle SLL Certificate, if they are provided = use them, else = self sign a certificate on the fly
        if self.conf.CERT_FILE is None or self.conf.KEY_FILE is None:
            self.logger.error(f"Provided CERT OR KEY file not found :  {self.conf.CERT_FILE} and {self.conf.KEY_FILE}")
            self.app.run(ssl_context='adhoc')
        else:
            self.logger.info(f"Provided CERT OR KEY file used : {self.conf.CERT_FILE} and {self.conf.KEY_FILE}")
            self.app.run(ssl_context=(str(self.conf.CERT_FILE), str(self.conf.KEY_FILE)))  # ssl_context='adhoc')

    def add_all_endpoints(self):
        # Add root endpoint
        self.add_endpoint(endpoint="/", endpoint_name="/", handler=self.ping)

        # Add action endpoints
        self.add_endpoint(endpoint="/add_picture", endpoint_name="/add_picture", handler=self.add_picture)
        self.add_endpoint(endpoint="/request_similar_picture", endpoint_name="/request_similar_picture", handler=self.request_similar_picture)
        self.add_endpoint(endpoint="/is_ready", endpoint_name="/is_ready", handler=self.is_ready)
        self.add_endpoint(endpoint="/get_results", endpoint_name="/get_results", handler=self.get_results)
        self.add_endpoint(endpoint="/export_db", endpoint_name="/export_db", handler=self.export_db_as_graphe)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=['GET', 'POST', 'PUT'])

    # ==================== ------ API Calls ------- ====================

    def ping(self, *args):
        result_json = {}
        result_json["Called_function"] = "ping"
        result_json = self.add_std_info(result_json)

        result_json["Status"] = "The API is ALIVE :)"
        # Note that "flask.request" is a global object, but is linked to the local context by flask. No worries :)

        return result_json
        # Test it with curl 127.0.0.1:5000

    def add_picture(self):
        result_json = {}
        result_json["Called_function"] = "add_picture"
        result_json = self.add_std_info(result_json)

        # Answer to PUT HTTP request
        if flask.request.method == 'PUT':
            try:
                # Received : werkzeug.datastructures.FileStorage. Should use ".read()" to get picture's value
                f = flask.request.files['image']
                self.logger.debug(f"Image received in server : {type(f)} ")  # {f.read()}

                # Compute input picture hash and convert to BMP
                f_hash = id_generator.get_SHA1(f)
                f_bmp = id_generator.convert_to_bmp(f)  # Returns a bytes array
                self.logger.debug(f"Image transformed in BMP in server : {type(f_bmp)} ")  # {f_bmp}

                # Save received picture to disk
                picture_import_export.save_picture(f_bmp, get_homedir() / 'datasets' / 'received_pictures' / (str(f_hash) + '.bmp'))
                # If the filename need to be used : secure_filename(f.filename)

                # Enqueue picture to processing
                self.logger.debug(f"Adding to feature queue : {f_hash} ")  # {f_bmp}
                self.database_worker.add_to_queue(self.database_worker.cache_db_decode, queue_name="feature_to_add", id=f_hash, dict_to_store={"img": f_bmp})

                result_json["Status"] = "Success"
                result_json["img_id"] = f_hash
            except Exception as e:
                self.logger.error(f"Error during PUT handling {e}")
                result_json["Status"] = "Failure"
                result_json["Error"] = "Error during Hash computation or database adding"
        else:
            result_json["Status"] = "Failure"
            result_json["Error"] = "BAD METHOD : use PUT instead of GET, POST, ..."

        return result_json
        # Test it with curl 127.0.0.1:5000/add_pict

    def request_similar_picture(self):
        result_json = {}
        result_json["Called_function"] = "request_similar_picture"
        result_json = self.add_std_info(result_json)

        # Answer to PUT HTTP request
        if flask.request.method == 'POST':
            try:
                # Received : werkzeug.datastructures.FileStorage. Should use ".read()" to get picture's value
                f = flask.request.files['image']
                self.logger.debug(f"Image received in server : {type(f)} ")  # {f.read()}

                # Compute input picture hash and convert to BMP
                f_hash = id_generator.get_SHA1(f)
                f_bmp = id_generator.convert_to_bmp(f)  # Returns a bytes array
                self.logger.debug(f"Image transformed in BMP in server : {type(f_bmp)} ")  # {f_bmp}

                # Save received picture to disk
                picture_import_export.save_picture(f_bmp, get_homedir() / 'datasets' / 'received_pictures' / (str(f_hash) + '.bmp'))
                # If the filename need to be used : secure_filename(f.filename)

                # TODO : Create request UUID ? Or keep image hash ?

                # Enqueue picture to processing
                self.logger.debug(f"Adding to feature queue : {f_hash} ")  # {f_bmp}
                self.database_worker.add_to_queue(self.database_worker.cache_db_decode, queue_name="feature_to_request", id=f_hash, dict_to_store={"img": f_bmp})

                result_json["Status"] = "Success"
                result_json["request_id"] = f_hash
            except Exception as e:
                self.logger.error(f"Error during PUT handling {e}")
                result_json["Status"] = "Failure"
                result_json["Error"] = "Error during Hash computation or database request"
        else:
            result_json["Status"] = "Failure"
            result_json["Error"] = "BAD METHOD : use POST instead of GET, PUT, ..."

        return result_json
        # Test it with curl 127.0.0.1:5000/request_similar_picture

    def is_ready(self):
        result_json = {}
        result_json["Called_function"] = "is_ready"
        result_json = self.add_std_info(result_json)

        # Answer to PUT HTTP request
        if flask.request.method == 'GET':
            try:
                # Received : werkzeug.datastructures.FileStorage. Should use ".read()" to get picture's value
                id = flask.request.args.get('request_id')
                self.logger.debug(f"Request ID to be checked if ready in server : {type(id)} ==> {id} ")  # {f.read()}

                # Fetch results
                # TODO : Special function for "cleaner/more performant" check ?
                _ = self.database_worker.get_request_result(self.database_worker.cache_db_no_decode, id)

                result_json["Status"] = "Success"
                result_json["request_id"] = id
                result_json["is_ready"] = True
            except Exception as e:
                self.logger.error(f"Normal error during GET handling ('is_ready' request) {e}")
                result_json["Status"] = "Failure"
                result_json["Error"] = "Error during database request"
                result_json["is_ready"] = False
        else:
            result_json["Status"] = "Failure"
            result_json["Error"] = "BAD METHOD : use GET instead of POST, PUT, ..."

        return result_json
        # Test it with curl 127.0.0.1:5000/is_ready

    def get_results(self):
        result_json = {}
        result_json["Called_function"] = "get_results"
        result_json = self.add_std_info(result_json)

        # Answer to PUT HTTP request
        if flask.request.method == 'GET':
            try:
                # Received : werkzeug.datastructures.FileStorage. Should use ".read()" to get picture's value
                id = flask.request.args.get('request_id')
                self.logger.debug(f"Request ID to be answered in server : {type(id)} ==> {id} ")  # {f.read()}

                # Fetch results
                result_dict = self.database_worker.get_request_result(self.database_worker.cache_db_no_decode, id)

                result_json["Status"] = "Success"
                result_json["request_id"] = id
                result_json["results"] = result_dict
            except Exception as e:
                self.logger.error(f"Error during GET handling {e}")
                result_json["Status"] = "Failure"
                result_json["Error"] = "Error during Hash computation or database request"
        else:
            result_json["Status"] = "Failure"
            result_json["Error"] = "BAD METHOD : use GET instead of POST, PUT, ..."

        return result_json
        # Test it with curl 127.0.0.1:5000/get_results

    def export_db_as_graphe(self):
        result_json = {}
        result_json["Called_function"] = "export_db"
        result_json = self.add_std_info(result_json)

        # Answer to PUT HTTP request
        if flask.request.method == 'GET':
            try:
                # Request export of the database and save it as a json graph
                self.db_utils = db_utils.DBUtilities(db_access_decode=self.database_worker.storage_db_decode, db_access_no_decode=self.database_worker.storage_db_no_decode)
                graphe = self.db_utils.get_db_graphe()

                # Save to file
                json_import_export.save_json(graphe, get_homedir() / "export_folder" / "db_graphe.json")

                result_json["Status"] = "Success"
                result_json["db"] = graphe
            except Exception as e:
                self.logger.error(f"Error during GET handling {e}")
                result_json["Status"] = "Failure"
                result_json["Error"] = "Error during db exportation to file"
        else:
            result_json["Status"] = "Failure"
            result_json["Error"] = "BAD METHOD : use POST instead of GET, PUT, ..."

        return result_json
        # Test it with curl 127.0.0.1:5000

    @staticmethod
    def add_std_info(result_json):
        result_json["Call_method"] = flask.request.method  # 'GET' or 'POST' ...
        result_json["Call_time"] = time.ctime()  # 'GET' or 'POST' ...

        return result_json


# Launcher for this worker. Launch this file to launch a worker
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch Flask API on server side')
    parser.add_argument("-dbc", '--database_configuration_file', dest="db_conf", type=dir_path, help='DB_configuration_file stored as json. Path')
    parser.add_argument("-wsc", '--webservice_configuration_file', dest="ws_conf", type=dir_path, help='WebService_configuration_file stored as json. Path')
    args = parser.parse_args()

    # Load the provided configuration file and create back the Configuration Object
    db_conf = database_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.db_conf)))
    ws_conf = webservice_conf.parse_from_dict(json_import_export.load_json(pathlib.Path(args.ws_conf)))

    # Create the Flask API and run it
    # Create Flask endpoint from configuration files
    api = FlaskAppWrapper('api', ws_conf=ws_conf, db_conf=db_conf)
    api.add_all_endpoints()

    # Run Flask API endpoint
    api.run()  # debug=True
