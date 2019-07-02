#!/bin/bash

set -e
set -x

# ../../redis/src/
redis-server ./test.conf
# Prevent old halt key to stop workers on launch
redis-cli -s ./../../database_sockets/test.sock del halt