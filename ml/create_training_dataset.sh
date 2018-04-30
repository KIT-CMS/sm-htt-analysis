#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

mkdir -p ml/${ERA}_${CHANNEL}

python ml/write_dataset_config.py \
    --channel ${CHANNEL} \
    --base-path $ARTUS_OUTPUTS \
    --database $KAPPA_DATABASE \
    --output-path $PWD/ml/${ERA}_${CHANNEL} \
    --output-filename training_dataset.root \
    --tree-path ${CHANNEL}_nominal/ntuple \
    --event-branch event \
    --training-weight-branch training_weight \
    --output-config ml/${ERA}_${CHANNEL}/dataset_config.yaml

./htt-ml/dataset/create_training_dataset.py ml/${ERA}_${CHANNEL}/dataset_config.yaml
