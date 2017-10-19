#!/bin/bash

CHANNEL="mt"

python ml/write_dataset_config.py \
    --channel ${CHANNEL} \
    --base-path /storage/jbod/wunsch/htt_2017-06-21_eleScale \
    --database /portal/ekpbms3/home/wunsch/CMSSW_7_4_7/src/Kappa/Skimming/data/datasets.json \
    --output-path $PWD/ml \
    --output-filename ${CHANNEL}_training_dataset.root \
    --tree-path ${CHANNEL}_nominal/ntuple \
    --event-branch event \
    --training-weight-branch training_weight \
    --output-config ml/${CHANNEL}_dataset_config.yaml

./htt-ml/dataset/create_training_dataset.py ml/${CHANNEL}_dataset.yaml
