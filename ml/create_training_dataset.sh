#!/bin/bash

CHANNEL=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

mkdir -p ml/${CHANNEL}

python ml/write_dataset_config.py \
    --channel ${CHANNEL} \
    --base-path /storage/jbod/wunsch/Run2Analysis_alex \
    --database /portal/ekpbms3/home/wunsch/CMSSW_7_4_7/src/Kappa/Skimming/data/datasets.json \
    --output-path $PWD/ml/mt \
    --output-filename ${CHANNEL}_training_dataset.root \
    --tree-path ${CHANNEL}_nominal/ntuple \
    --event-branch event \
    --training-weight-branch training_weight \
    --output-config ml/${CHANNEL}/dataset_config.yaml

./htt-ml/dataset/create_training_dataset.py ml/${CHANNEL}/dataset_config.yaml
