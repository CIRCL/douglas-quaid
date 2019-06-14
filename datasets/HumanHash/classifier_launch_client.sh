#!/bin/bash

set -e
set -x

echo ‘Establishing proxy. Please leave the screen with "CTRL+A+D" ’
screen -dm -S Proxy_ssh_to_CRDB ssh -D 8080 crdb
echo ‘Please configure proxy in your default browser and then press key to continue.’
read -p "Press any key to continue... " -n1 -s
echo 'Accessing website ...'
xdg-open 'http://149.13.33.83:80'
echo ‘If you then want to kill the proxy .. press a key’
read -p "Press any key to continue... " -n1 -s
screen -X -S Proxy_ssh_to_CRDB quit