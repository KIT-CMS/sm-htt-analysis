#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ARTUS_OUTPUTS=$1
KAPPA_DATABASE=$2
ET_TRAINING=$3
MT_TRAINING=$4

python shapes/calculate_binning.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --output shapes/binning.yaml \
    --et-training $ET_TRAINING \
    --mt-training $MT_TRAINING
