#!/bin/bash

set -e
set -x

echo ‘Launching docker service ’
sudo service docker start
echo ‘Current working and old dockers : ’
docker ps -a
echo ‘Please check if no docker is already running on port 80’
read -p "Press any key to continue... " -n1 -s
echo ‘Launching docker’
screen -S docker_classifcation sudo docker run -d -p 80:80 dataturks/dataturks:3.3.0 --name=classification_docker
echo ‘Please proxy on : ’
ip a | grep "scope global" | grep -Po '(?<=inet )[\d.]+'