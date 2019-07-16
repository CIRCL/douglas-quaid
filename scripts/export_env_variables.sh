#!/bin/sh
set -e
set -x

# See : https://askubuntu.com/questions/53177/bash-script-to-set-environment-variables-not-working
echo "Launch with : # source ./export_env_variables.sh"

export PYTHONPATH=${PYTHONPATH}:${PWD}
#export PYTHONPATH=${PYTHONPATH}:"/home/user/Desktop/douglas-quaid"
export CARLHAUSER_HOME=${PWD}
#export CARLHAUSER_HOME='/home/user/Desktop/douglas-quaid'