# ==================== ------ STD LIBRARIES ------- ====================
import pathlib

import carlhauser_server.Configuration.database_conf as database_conf
from common.environment_variable import load_server_logging_conf_file

load_server_logging_conf_file()


# ==================== ------ PERSONAL LIBRARIES ------- ====================


class TestInstance_database_conf(database_conf.Default_database_conf):
    def __init__(self):
        super().__init__()

        # ============================== SCRIPTS ==============================
        self.DB_SCRIPTS_PATH = pathlib.Path('carlhauser_server', 'Data', 'database_scripts')
        # Cache, storage and test scripts directories
        self.DB_SCRIPTS_PATH_CACHE = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'test')
        self.DB_SCRIPTS_PATH_STORAGE = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'test')
        self.DB_SCRIPTS_PATH_TEST = pathlib.Path('carlhauser_server', 'Data', 'database_scripts', 'test')

        # ============================== SOCKETS ==============================
        self.DB_SOCKETS_PATH = pathlib.Path('carlhauser_server', 'Data', 'database_sockets')
        # Cache, storage and test scripts directories
        self.DB_SOCKETS_PATH_CACHE = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'test.sock')
        self.DB_SOCKETS_PATH_STORAGE = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'test.sock')
        self.DB_SOCKETS_PATH_TEST = pathlib.Path('carlhauser_server', 'Data', 'database_sockets', 'test.sock')

        self.ONLY_TEST_DB: bool = True
