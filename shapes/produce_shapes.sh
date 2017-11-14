#!/bin/bash

ARTUS_OUTPUTS=$1
KAPPA_DATABASE=$2
BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

# Calculate binning from data distributions
# NOTE: Binning is now committed in repository.
#./shapes/calculate_binning.sh $ARTUS_OUTPUTS $KAPPA_DATABASE $ET_TRAINING $MT_TRAINING

# Produce shapes
python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING
