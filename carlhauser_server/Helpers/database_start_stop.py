#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import subprocess
import pathlib
import time
import redis
import logging
# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir

'''
>>> r = redis.Redis(host='localhost', port=6379, db=0)
>>> r.set('foo', 'bar')
True
>>> r.get('foo')

'''

database_scripts_path = pathlib.Path('carlhauser_server', 'Helpers', 'database_scripts')
database_sockets_path = pathlib.Path('carlhauser_server', 'Helpers', 'database_sockets')
database_data_path = pathlib.Path('carlhauser_server', 'Helpers', 'database_data')


def get_socket_path(name: str) -> str:
    # Redis is configured to allow connection from/to Unix socket
    # Unix sockets paths for Redis are defined in cache.conf and storage.conf
    mapping = {
        'cache': get_homedir() / database_sockets_path / pathlib.Path('cache.sock'),
        'storage': get_homedir() / database_sockets_path / pathlib.Path('storage.sock'),
    }
    return str(get_homedir() / mapping[name])


def check_running(name: str) -> bool:
    socket_path = get_socket_path(name)

    print(socket_path)
    try:
        r = redis.Redis(unix_socket_path=socket_path)
        if r.ping():
            return True
    except Exception as e:
        # logger = logging.getLogger(__name__)
        # logger.error(f"PING got no answer. Invalid socket. {e}")
        return False


# ==================== ------ CACHE MNGT ------- ====================


def launch_cache():
    # Launch cache instance of redis. Uses a launch script
    if not check_running('cache'):
        script_path = get_homedir() / database_scripts_path / pathlib.Path("run_redis_cache.sh")
        subprocess.Popen([str(script_path)], cwd=(get_homedir() / database_scripts_path))


def shutdown_cache():
    script_path = get_homedir() / database_scripts_path / pathlib.Path("shutdown_redis_cache.sh")
    subprocess.Popen([str(script_path)], cwd=(get_homedir() / database_scripts_path))


# ==================== ------ STORAGE MNGT ------- ====================

def launch_storage():
    # Launch storage instance of redis. Uses a launch script
    if not check_running('storage'):
        script_path = get_homedir() / database_scripts_path / pathlib.Path("run_redis_storage.sh")
        subprocess.Popen([str(script_path)], cwd=(get_homedir() / database_scripts_path))


def shutdown_storage():
    script_path = get_homedir() / database_scripts_path / pathlib.Path("shutdown_redis_storage.sh")
    subprocess.Popen([str(script_path)], cwd=(get_homedir() / database_scripts_path))


# ==================== ------ ALL MNGT ------- ====================

def launch_all_redis():
    # Launch the cache instance of redis, and the storage instance of redis
    launch_cache()
    launch_storage()


def check_all_redis(stop=False):
    backends = [['cache', False], ['storage', False]]
    while True:
        for b in backends:
            try:
                b[1] = check_running(b[0])
            except Exception:
                b[1] = False
        if stop:
            if not any(b[1] for b in backends):
                break
        else:
            if all(b[1] for b in backends):
                break
        for b in backends:
            if not stop and not b[1]:
                print(f"Waiting on {b[0]}")
            if stop and b[1]:
                print(f"Waiting on {b[0]}")
        time.sleep(1)


def stop_all_redis():
    shutdown_cache()
    shutdown_storage()
