#!/bin/bash

# set -e
# set -x

# Launching docker service
sudo service docker start

# Current working and old dockers :
sudo docker ps -a

# Please check if no docker is already running on port 80
read -p "Press any key to continue... " -n1 -s

# Load docker
sudo docker load --input /home/vincent/dataturks/dataturks_docker.tar

# Launching docker
sudo docker run --name=classification_docker -d -p 80:80 dataturks/dataturks:3.3.0

cd /home/vincent/AIL_dataset_checked/
# Serving pictures
screen -dm -S picture_serving_python python -m SimpleHTTPServer 8000

# Launch docker commiter
screen -S python_docker_saver pipenv run python3 ./docker_committer.py -n classification_docker_from_save -s 900 -l 5


# Please proxy on
ip a | grep "scope global" | grep -Po '(?<=inet )[\d.]+'

# urlify dataset
python3 ./urlifier.py -p ./../../../AIL_dataset_checked/ -i 149.13.33.83 -t 8000/img

# Get a shell on the docker
sudo docker exec -it classification_docker /bin/bash

# Install things to modify apache files
apt-get -y install vim
vim /etc/apache2/sites-available/000-default.conf

# Add (NOT WORKING : DENIED ACCESS TO LOCALHOST FROM APACHE IN DOCKER) : the python server is running on the local machine too
   ProxyPass        /img/ http://localhost:8000/
   ProxyPassReverse /img/ http://localhost:8000/

# Working : 14xxx being the ip of the machine on which is running the python server.
   ProxyPass        /img/ http://149.13.33.83:8000/
   ProxyPassReverse /img/ http://149.13.33.83:8000/

# Reload config
# apache2ctl -S
/etc/init.d/apache2 reload

# See logs
tail -100 /var/log/apache2/other_vhosts_access.log

# Kill docker
sudo docker stop classification_docker

# List loaded images
docker images

# Rejected from stopping docker ? Add yourself to docker group !
sudo usermod -aG docker $USER

# Clean up and remove all dockers
sudo docker ps -aq | xargs docker rm