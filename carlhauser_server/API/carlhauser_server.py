#!flask/bin/python

# Inspired from : https://github.com/D4-project/IPASN-History/blob/master/website/web/__init__.py

# ==================== ------ STD LIBRARIES ------- ====================
import flask
import sys, os

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
import carlhauser_server.Configuration.webservice_conf as webservice_conf

# ==================== ------ Flask API definition ------- ====================

class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        # self.response = flask.Response("Welcome to carl-hauser", status=200, headers={})

    def __call__(self, *args):
        # Perform the action
        answer = self.action()
        # Create the answer (bundle it in a correctly formatted HTTP answer)
        self.response = flask.Response(answer, status=200, headers={})
        # Send it
        return self.response


class FlaskAppWrapper(object):
    def __init__(self, name, conf:webservice_conf):
        self.app = flask.Flask(name)
        self.conf = conf

    def run(self):
        self.app.run()

    def add_all_endpoints(self):
        # Add root endpoint
        self.add_endpoint(endpoint="/", endpoint_name="/", handler=self.action)

        # Add action endpoints
        self.add_endpoint(endpoint="/add_picture", endpoint_name="/add_picture", handler=self.add_picture)
        self.add_endpoint(endpoint="/request_similar_picture", endpoint_name="/request_similar_picture", handler=self.request_similar_picture)
        self.add_endpoint(endpoint="/get_results", endpoint_name="/get_results", handler=self.get_results)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))

    # ==================== ------ API Calls ------- ====================
    def action(self):
        # Dummy action
        return "action"

    def add_picture(self):
        # Dummy action
        return "add_picture"

    def request_similar_picture(self):
        # Dummy action
        return "request_similar_picture"

    def get_results(self):
        # Dummy action
        return "get_results"

