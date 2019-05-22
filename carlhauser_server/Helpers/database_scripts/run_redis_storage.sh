#!/bin/bash

set -e
set -x

# ../../redis/src/
redis-server ./storage.conf
# Prevent old halt key to stop workers on launch
redis-cli -s ./../database_sockets/storage.sock del halt

