#!/bin/bash

set -e
set -x

# ../../redis/src/redis-cli
redis-cli -s ./../../database_sockets/cache.sock FLUSHALL
redis-cli -s ./../../database_sockets/cache.sock SET halt ''
redis-cli -s ./../../database_sockets/cache.sock del halt
