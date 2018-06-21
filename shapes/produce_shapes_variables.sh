#!/bin/bash

BINNING=plotting/custom_binning.yaml #shapes/binning.yaml
ERA=$1
CHANNELS=$2
VARIABLE=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions
# NOTE: Binning is committed in this repository.
#./shapes/calculate_binning.sh et
#./shapes/calculate_binning.sh mt
#./shapes/calculate_binning.sh tt

# Produce shapes


python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --gof-channel $CHANNELS \
    --gof-variable $VARIABLE \
    --era $ERA \
    --tag ${ERA}_${CHANNELS}
