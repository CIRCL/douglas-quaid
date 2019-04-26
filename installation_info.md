## Installation
### Library testing framework

#### Installation

> \# Install system dependency  
> sudo apt-get install libsm6 cmake python3.7 python3.7-dev 
> 
> \# Get repository  
> git clone https://github.com/Vincent-CIRCL/carl-hauser.git    
> 
> \# Prepare pipenv  
> sudo apt install python3-pip  
> sudo pip3 install pipenv  
> 
> \# Pipenv setup   
> cd ./carl-hauser/ 
> pipenv install --ignore-pipfile   
> 
> \# TLSH instructions  
> cd ./lib_testing_area/TLSH/   
> chmod +x ./install.sh 
> install.sh    

#### Dataset instruction
From root folder :

You can put pictures in "./datasets" folder. If not present, you can create it.
Default folder is named "./datasets/raw_phishing"

#### Launch instruction
From root folder :

> cd ./lib_testing_area/   
> python3 ./launcher.py