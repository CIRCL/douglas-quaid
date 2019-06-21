## Installation

Just follow instruction, top to bottom

Tested on Ubuntu Server 18.04 LTS, clean install.

### Core product

> \# Install system dependency  
> sudo apt-get install python3.7 python3.7-dev libsm6 libxrender1 cmake 
>
> \# Prepare pipenv  
> sudo apt install python3-pip  
> sudo pip3 install pipenv  
> 
> \# Get repository  
> git clone https://github.com/CIRCL/douglas-quaid.git  
> 
> \# Pipenv setup   
> cd ./douglas-quaid/   
> pipenv install --ignore-pipfile       
>
> \# Setup your carlhauser path 
> export CARLHAUSER_HOME='/home/user/douglas-quaid'     
> PLEASE BE AWARE TO CHANGE THE PATH TO THE CURRENT INSTALLATION PATH.  
> THIS IS ABSOLUTELY REQUIRED FOR THE LIBRARY TO WORK !     

### Dependencies 

#### TLSH
> \# TLSH instructions  
> \# Go in the pipenv shell 
> pipenv shell  
> chmod +x ./tlsh_install.sh    
> sudo ./tlsh_install.sh        

#### Redis
> \# Install system dependency  
> sudo apt-get install redis


### Launch instruction
From root folder :

#### Server side API
> \# Launch server side, with flask to receive API calls     
> cd ./carlhauser_server
> pipenv run python3 ./core.py   
OR  
> screen -S server-api pipenv run python3 ./core.py 

You should get an output like this one on launch if everything fine. (beaware, it may not be exactly up to date) : 
```bash
(...)
XXX,145 - carlhauser_server.DatabaseAccessor.database_worker - INFO - Creation of a Database Accessor Worker
XXX,145 - root - DEBUG - File loaded from /home/user/douglas-quaid/tmp_fe_conf.json.
XXX,146 - carlhauser_server.DatabaseAccessor.database_worker - INFO - Creation of a Database Accessor Worker
XXX,146 - carlhauser_server.DistanceEngine.distance_engine - INFO - ... which is a Distance Engine
XXX,146 - carlhauser_server.DistanceEngine.distance_hash - INFO - Creation of a Distance Hash Engine
XXX,146 - carlhauser_server.DistanceEngine.distance_orb - INFO - Creation of a Distance ORB Engine
XXX,146 - carlhauser_server.DistanceEngine.merging_engine - INFO - Creation of a Distance ORB Engine
XXX,146 - carlhauser_server.DatabaseAccessor.database_worker - INFO - Launching Database_Adder
XXX,146 - carlhauser_server.FeatureExtractor.picture_hasher - INFO - Creation of a Picture Hasher
XXX,146 - carlhauser_server.FeatureExtractor.picture_orber - INFO - Creation of a Picture Hasher
XXX,146 - carlhauser_server.DatabaseAccessor.database_worker - INFO - Launching Feature_Worker
XXX,155 - root - DEBUG - File loaded from /home/user/douglas-quaid/tmp_db_conf.json.
XXX,155 - root - DEBUG - File loaded from /home/user/douglas-quaid/tmp_fe_conf.json.
XXX,155 - carlhauser_server.DatabaseAccessor.database_worker - INFO - Creation of a Database Accessor Worker
XXX,156 - carlhauser_server.FeatureExtractor.picture_hasher - INFO - Creation of a Picture Hasher
XXX,156 - carlhauser_server.FeatureExtractor.picture_orber - INFO - Creation of a Picture Hasher
XXX,156 - carlhauser_server.DatabaseAccessor.database_worker - INFO - Launching Feature_Worker
XXX,296 - root - DEBUG - File loaded from /home/user/douglas-quaid/tmp_db_conf.json.
XXX,296 - root - DEBUG - File loaded from /home/user/douglas-quaid/tmp_ws_conf.json.
XXX,299 - carlhauser_server.DatabaseAccessor.database_worker - INFO - Creation of a Database Accessor Worker
XXX,304 - __main__ - INFO - Provided CERT OR KEY file used : /home/user/douglas-quaid/carlhauser_server/cert.pem and /home/user/douglas-quaid/carlhauser_server/key.pem
 * Serving Flask app "api" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
XXX,314 - werkzeug - INFO -  * Running on https://127.0.0.1:5000/ (Press CTRL+C to quit)
Press any key to stop ... 
```

#### Client side API
> \# Launch client side, to send API calls     
> cd ./carlhauser_client
> pipenv run python3 ./core.py  
OR  
> screen -S client-api pipenv run python3 ./core.py 
