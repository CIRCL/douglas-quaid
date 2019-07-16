#!/bin/sh

pkill redis
pkill redis
pkill redis
pkill redis
rm ./carlhauser_server/Data/database_data/cache.log
rm ./carlhauser_server/Data/database_data/storage.log
rm ./carlhauser_server/Data/database_data/test.log
rm ./carlhauser_server/Data/database_data/cache_dump.rdb
rm ./carlhauser_server/Data/database_data/storage_dump.rdb
rm ./carlhauser_server/Data/database_data/test_dump.rdb
rm ./tmp_db_conf.json
rm ./tmp_dist_conf.json
rm ./tmp_fe_conf.json
rm ./tmp_ws_conf.json
echo "Cleaned ! Ready."
