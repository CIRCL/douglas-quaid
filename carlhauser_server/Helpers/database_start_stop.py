#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import subprocess
import pathlib
import time
import redis

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))

from carlhauser_server.Helpers.environment_variable import get_homedir

'''
>>> r = redis.Redis(host='localhost', port=6379, db=0)
>>> r.set('foo', 'bar')
True
>>> r.get('foo')

'''


def get_socket_path(name: str) -> str:
    mapping = {
        'cache': pathlib.Path('carlhauser_server', 'Helpers', 'database_sockets', 'cache.sock'),
        'storage': pathlib.Path('carlhauser_server', 'Helpers', 'database_sockets', 'storage.sock'),
    }
    return str(get_homedir() / mapping[name])


def check_running(name: str) -> bool:
    socket_path = get_socket_path(name)


# ==================== ------ CACHE MNGT ------- ====================

def launch_cache(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    if not check_running('cache'):
        subprocess.Popen(["./run_redis_cache.sh"], cwd=(storage_directory / 'cache'))


def shutdown_cache(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    subprocess.Popen(["./shutdown_redis_cache.sh"], cwd=(storage_directory / 'cache'))


# ==================== ------ STORAGE MNGT ------- ====================

def launch_storage(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    if not check_running('storage'):
        subprocess.Popen(["./run_redis_storage.sh"], cwd=(storage_directory / 'storage'))


def shutdown_storage(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    subprocess.Popen(["./shutdown_redis_storage.sh"], cwd=(storage_directory / 'storage'))

# ==================== ------ ALL MNGT ------- ====================

def launch_all_redis():
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
