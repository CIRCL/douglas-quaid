#!/bin/bash
git clone https://github.com/trendmicro/tlsh
cd ./tlsh
./make.sh
cd py_ext/
python3 ./setup.py build
python3 ./setup.py install
cd ../Testing
./python_test.sh