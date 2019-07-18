#!/bin/sh

echo "Killing databases ... "
pkill redis
pkill redis
pkill redis
pkill redis
sleep 5

echo "Wiping databases ... "
rm ./carlhauser_server/Data/database_data/cache.log
rm ./carlhauser_server/Data/database_data/storage.log
rm ./carlhauser_server/Data/database_data/test.log
rm ./carlhauser_server/Data/database_data/cache_dump.rdb
rm ./carlhauser_server/Data/database_data/storage_dump.rdb
rm ./carlhauser_server/Data/database_data/test_dump.rdb
sleep 1

echo "Wiping configuration files ... "
rm ./tmp_db_conf.json
rm ./tmp_dist_conf.json
rm ./tmp_fe_conf.json
rm ./tmp_ws_conf.json

echo "Killing workers ... "
kill $(ps -ef | grep "python3 /home/user/Desktop/douglas-quaid" | awk '{ print $2 }')
echo "Cleaned ! Ready."
