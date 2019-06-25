#!/bin/bash

BINNING=shapes/binning.yaml
ERA=$1
CHANNELS=${@:2}

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python shapes/produce_shapes_$ERA.py \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --era $ERA \
    --tag $ERA \
    --num-threads 32 \
    --QCD-extrap-fit

# Normalize fake-factor shapes to nominal
python fake-factor-application/normalize_shifts.py ${ERA}_shapes.root