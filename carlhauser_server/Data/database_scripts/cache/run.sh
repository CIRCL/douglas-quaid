#!/bin/bash

set -e
set -x

# ../../redis/src/
redis-server ./cache.conf
/bin/sleep 1
# Prevent old halt key to stop workers on launch
redis-cli -s ./../../database_sockets/cache.sock del halt
