#!/bin/bash

set -e
set -x

echo ‘Establishing proxy ’
ssh -D 8080 crdb
echo ‘Please configure proxy in your default browser and then press key to continue.’
read -p "Press any key to continue... " -n1 -s
echo ‘Accessing website ...'
xdg-open ‘http://149.13.33.83:8080’