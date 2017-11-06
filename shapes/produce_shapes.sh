#!/bin/bash

ARTUS_OUTPUTS=$1
KAPPA_DATABASE=$2
BINNING=shapes/binning.yaml
ET_TRAINING=keras20
MT_TRAINING=keras20

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

# Calculate binning from data distributions
# NOTE: Binning is now committed in repository.
#./shapes/calculate_binning.sh $ARTUS_OUTPUTS $KAPPA_DATABASE $ET_TRAINING $MT_TRAINING

# Produce shapes
python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --et-training $ET_TRAINING \
    --mt-training $MT_TRAINING
