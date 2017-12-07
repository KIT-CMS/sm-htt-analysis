#!/bin/bash

BINNING=shapes/binning.yaml
CHANNELS=$@

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

# Calculate binning from data distributions
# NOTE: Binning is now committed in repository.
#./shapes/calculate_binning.sh $ARTUS_OUTPUTS $KAPPA_DATABASE $ET_TRAINING $MT_TRAINING

# Produce shapes
python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --QCD-extrap-fit
