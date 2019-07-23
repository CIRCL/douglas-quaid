#!/bin/sh
set -e
set -x

# Phishing dataset
python3 ./common/Calibrator/threshold_calibrator.py -s ./datasets/raw_phishing_full/ -gt ./datasets/clustered.json -d ./datasets/OUTPUT_EXPLANATION/ from_cmd_args -AFPR 0.1 -AFNR 0.1