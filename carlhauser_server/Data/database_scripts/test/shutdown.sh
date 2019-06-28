#!/bin/bash

set -e
set -x

# ../../redis/src/redis-cli
redis-cli -s ./test.sock FLUSHALL
redis-cli -s ./test.sock shutdown
