#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ------ STD LIBRARIES ------- ====================
import sys, os
import subprocess
import pathlib
# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))





# ==================== ------ CACHE MNGT ------- ====================

def launch_cache(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    if not check_running('cache'):
        subprocess.Popen(["./run_redis.sh"], cwd=(storage_directory / 'cache'))


def shutdown_cache(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    subprocess.Popen(["./shutdown_redis.sh"], cwd=(storage_directory / 'cache'))


# ==================== ------ STORAGE MNGT ------- ====================

def launch_storage(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    if not check_running('storage'):
        subprocess.Popen(["./run_ardb.sh"], cwd=(storage_directory / 'storage'))


def shutdown_storage(storage_directory: pathlib.Path = None):
    if not storage_directory:
        storage_directory = get_homedir()
    subprocess.Popen(["./shutdown_ardb.sh"], cwd=(storage_directory / 'storage'))


# ==================== ------ ALL MNGT ------- ====================

def launch_all():
    launch_cache()
    launch_storage()


def check_all(stop=False):
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


def stop_all():
    shutdown_cache()
    shutdown_storage()
