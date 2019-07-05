# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
from collections import namedtuple

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_server.Configuration.template_conf import JSON_parsable_Dict


class Default_database_conf(JSON_parsable_Dict):
    def __init__(self):
        # Please note that CERT and KEY files must be in carl-hauser/carlhauser_server (where the flask server is)

        # ============================== SCRIPTS ==============================
        self.DB_SCRIPTS_PATH: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_scripts')
        # Cache, storage and test scripts directories
        self.DB_SCRIPTS_PATH_CACHE: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'cache')
        self.DB_SCRIPTS_PATH_STORAGE: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'storage')
        self.DB_SCRIPTS_PATH_TEST: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'test')

        # ============================== SOCKETS ==============================
        self.DB_SOCKETS_PATH: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_sockets')
        # Cache, storage and test scripts directories
        self.DB_SOCKETS_PATH_CACHE: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'cache.sock')
        self.DB_SOCKETS_PATH_STORAGE: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'storage.sock')
        self.DB_SOCKETS_PATH_TEST: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'test.sock')

        # ============================== DB ==============================
        self.DB_DATA_PATH: pathlib.Path = pathlib.Path('carlhauser_server', 'Data', 'database_data')

        # ============================== DB PARAMETERS ==============================
        # Expiration time after which a add_request, computation_request, ... is removed (satisfied or not)
        self.REQUEST_EXPIRATION: int = 86400
        self.ANSWER_EXPIRATION: int = 86400

        # ============================== WORKERS PARAMETERS ==============================
        # NB of worker on launch
        self.ADDER_WORKER_NB: int = 2
        self.ADDER_WAIT_SEC: int = 1

        # NB of worker on launch
        self.REQUESTER_WORKER_NB: int = 2
        self.REQUESTER_WAIT_SEC: int = 1

        # ============================== TEST and EVALUATION PURPOSES ==============================
        # Nothing will be writen on storage or cache databases. Made for automatic evaluation, etc.
        self.ONLY_TEST_DB: bool = False


def parse_from_dict(conf):
    return namedtuple("Default_database_conf", conf.keys())(*conf.values())


# ==================== To string ====================

'''
    # Overwrite to print the content of the cluster instead of the cluster memory address
    def __repr__(self):
        return self.get_str()

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return ''.join(map(str, [' \nDB_SCRIPTS_PATH=', self.DB_SCRIPTS_PATH,
                                 ' \nDB_SCRIPTS_PATH_CACHE=', self.DB_SCRIPTS_PATH_CACHE,
                                 ' \nDB_SCRIPTS_PATH_STORAGE=', self.DB_SCRIPTS_PATH_STORAGE,
                                 ' \nDB_SCRIPTS_PATH_TEST=', self.DB_SCRIPTS_PATH_TEST,
                                 ' \nDB_SOCKETS_PATH=', self.DB_SOCKETS_PATH,
                                 ' \nDB_SOCKETS_PATH_CACHE=', self.DB_SOCKETS_PATH_CACHE,
                                 ' \nDB_SOCKETS_PATH_STORAGE=', self.DB_SOCKETS_PATH_STORAGE,
                                 ' \nDB_SOCKETS_PATH_TEST=', self.DB_SOCKETS_PATH_TEST,
                                 ' \nDB_DATA_PATH=', self.DB_DATA_PATH,
                                 ' \nREQUEST_EXPIRATION=', self.REQUEST_EXPIRATION,
                                 ' \nANSWER_EXPIRATION=', self.ANSWER_EXPIRATION,
                                 ' \nADDER_WORKER_NB=', self.ADDER_WORKER_NB,
                                 ' \nADDER_WAIT_SEC=', self.ADDER_WAIT_SEC,
                                 ' \nREQUESTER_WORKER_NB=', self.REQUESTER_WORKER_NB,
                                 ' \nREQUESTER_WAIT_SEC=', self.REQUESTER_WAIT_SEC]))

'''
