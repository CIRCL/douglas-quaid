#!/bin/bash

set -e
set -x

# ../../redis/src/redis-cli
redis-cli -s ./../../database_sockets/test.sock FLUSHALL
redis-cli -s ./../../database_sockets/test.sock shutdown
