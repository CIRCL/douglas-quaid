#!/bin/sh
set -e
set -x

echo PYTHONPATH=${PYTHONPATH}:${PWD} >.env        # create the file and write into
echo CARLHAUSER_HOME=$PWD >>.env    # append to the file