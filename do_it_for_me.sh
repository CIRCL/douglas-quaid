#!/bin/sh
set -e
set -x

python3 ./common/Calibrator/threshold_calibrator.py -s /home/user/Desktop/DATASETS/PHISHING/MINI_SAMPLED -gt /home/user/Desktop/DATASETS/PHISHING/PHISHING-DATASET-GT/DISTRIBUTED_visjs_graph.json -d /home/user/Desktop/douglas-quaid/datasets/OUTPUT_EXPLANATION/ from_cmd_args -AFPR 0.1 -AFNR 0.1

python3 ./carlhauser_server/instance_handler.py -fec ./datasets/OUTPUT_EXPLANATION/calibrated_db_conf.json -distc ./datasets/OUTPUT_EXPLANATION/dist_conf_calibrated.json

python3 ./carlhauser_client/EvaluationTools/SimilarityGraphExtractor/similarity_graph_extractor.py -s /home/user/Desktop/DATASETS/PHISHING/PHISHING-DATASET-DISTRIBUTED -gt /home/user/Desktop/DATASETS/PHISHING/PHISHING-DATASET-GT/DISTRIBUTED_visjs_graph.json -d /home/user/Desktop/douglas-quaid/datasets/OUTPUT_EVALUATION/

node server.js -i ./../DATASETS/PHISHING/PHISHING-DATASET-DISTRIBUTED -t ./../visjs_classificator/TMP -o ./../visjs_classificator/TMP -j ./../douglas-quaid/datasets/OUTPUT_EVALUATION/distance_graph.json

