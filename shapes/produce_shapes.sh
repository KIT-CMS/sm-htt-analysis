#!/bin/bash

BINNING=shapes/binning.yaml
ERA=$1
CHANNELS=${@:2}

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
for CHANNEL in $CHANNELS
do
    python shapes/produce_shapes.py \
        --directory $ARTUS_OUTPUTS \
        --et-friend-directory $ARTUS_FRIENDS_ET \
        --mt-friend-directory $ARTUS_FRIENDS_MT \
        --tt-friend-directory $ARTUS_FRIENDS_TT \
        --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
        --datasets $KAPPA_DATABASE \
        --binning $BINNING \
        --channels $CHANNEL \
        --era $ERA \
        --tag ${ERA}_${CHANNEL} \
        --num-threads 12 # & # NOTE: We are at the file descriptor limit.
    python fake-factors/normalize_shifts.py -i ${ERA}_${CHANNEL}_shapes.root
done

wait

hadd -f ${ERA}_shapes.root ${ERA}_*_shapes.root
