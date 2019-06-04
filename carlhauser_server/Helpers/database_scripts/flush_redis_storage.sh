#!/bin/bash

set -e
set -x

# ../../redis/src/redis-cli
redis-cli -s ./../database_sockets/storage.sock FLUSHALL
redis-cli -s ./../database_sockets/storage.sock SET halt ''
redis-cli -s ./../database_sockets/storage.sock del halt
