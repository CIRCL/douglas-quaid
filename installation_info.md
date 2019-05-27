## Installation

Just follow instruction, top to bottom

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

#### Client side API
> \# Launch client side, to send API calls     
> cd ./carlhauser_client
> pipenv run python3 ./core.py  
OR  
> screen -S client-api pipenv run python3 ./core.py 
