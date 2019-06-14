#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# See : https://github.com/docker/docker-py
import docker
import argparse
import pathlib
from collections import deque
import time
import datetime

'''
# Use append like before to add elements
numbers.append(99)  
numbers.append(15)  
numbers.append(82)  
numbers.append(50)  
numbers.append(47)

# You can pop like a stack
last_item = numbers.pop()  
print(last_item) # 47  
print(numbers) # deque([99, 15, 82, 50])

# You can dequeue like a queue
first_item = numbers.popleft()  
print(first_item) # 99  
print(numbers) # deque([15, 82, 50]) 
'''

### LAAAAUNCH WITH ROOT ACCESS !! or with user in docker group ####

class DockerCommmiter():

    def __init__(self, saves_limit):
        self.client = docker.from_env()
        self.deque_saves = deque()
        self.saves_limit = saves_limit
        self.current_save_id = 0

    def inifnite_commit_docker(self, docker_name, nb_secs):
        print("List of runing container :", self.client.containers.list())
        print("List of images :", self.client.images.list())

        while True :

            # Commit the docker
            self.commit_docker(docker_name)
            # Remove the old ones
            self.remove_too_old_images()

            # wait for next scheduled save time
            time.sleep(nb_secs)


    def commit_docker(self, docker_name ) -> str:
        commit_name = self.get_commit_name()

        print(f"Commiting : {commit_name}")
        tmp_image = self.client.containers.get(docker_name).commit(commit_name)

        self.deque_saves.append(tmp_image)

        return commit_name

    def get_commit_name(self):
        datetime_object = datetime.datetime.now()
        print("Current date : ", datetime_object)
        commit_name = "save_" + str(self.current_save_id) + str(datetime_object).replace(" ", "_").replace(":", "_").replace("-", "_").replace(".", "_")
        self.current_save_id += 1
        return commit_name

    def remove_too_old_images(self):

        if len(self.deque_saves) > self.saves_limit :
            image_to_remove = self.deque_saves.popleft()
            print(f"Too many saves. Removing save : {image_to_remove}")

            self.client.images.remove(image_to_remove.id)
        else :
            print(f"Save limit not reached for now, only {len(self.deque_saves)} saves")

'''
>>> client.images.remove(t.id)
>>> client.images.list()
[<Image: ''>, <Image: 'ubuntu:latest'>, <Image: 'rediscommander/redis-commander:latest'>]
>>> client.images.list()
[<Image: ''>, <Image: 'ubuntu:latest'>, <Image: 'rediscommander/redis-commander:latest'>]
>>> t = client.containers.get("musing_yonath").commit("test_image")
>>> t
<Image: 'test_image:latest'>
>>> client.images.list()
[<Image: 'test_image:latest'>, <Image: ''>, <Image: 'ubuntu:latest'>, <Image: 'rediscommander/redis-commander:latest'>]
>>> client.images.remove(t.id)
>>> client.images.list()
[<Image: ''>, <Image: 'ubuntu:latest'>, <Image: 'rediscommander/redis-commander:latest'>]

'''


# HOW TO USE :
# Launch your docker
# Launch the monitor :
# screen -S python_commiter python3 ./docker_committer.py -n <docker_name> -s 1500 -l 5


def main():
    # Usage example : python3 ./humanizer.py -p ./MINI_DATASET/
    parser = argparse.ArgumentParser(description='Regularly save docker provided as parameter')
    parser.add_argument('-n', '--name', dest='docker_name', action='store', type=str, default=1, help='Docker name to monitor')
    parser.add_argument('-s', '--sec', dest='seconds', action='store', type=int, default=1, help='Seconds between each commit')
    parser.add_argument('-l', '--limit', dest='save_limit', action='store', type=int, default=1, help='Number of saves to keep')
    parser.add_argument('--version', action='version', version='humanizer %s' % ("1.0.0"))

    args = parser.parse_args()
    dockermng = DockerCommmiter(args.save_limit)
    dockermng.inifnite_commit_docker(args.docker_name, args.seconds)


if __name__ == "__main__":
    main()
