#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python htt-ml/application/export_keras_to_json.py  ml/${ERA}_${CHANNEL}_training_custom_loss.yaml ml/${ERA}_${CHANNEL}_application.yaml
