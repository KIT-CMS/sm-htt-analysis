#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
NUM_THREADS=$4
BINNING=gof/${ERA}_binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions if file is not existent
if [ ! -f "$BINNING" ]
then
    python gof/calculate_binning.py \
        --era $ERA \
        --directory $ARTUS_OUTPUTS \
        --datasets $KAPPA_DATABASE \
        --output $BINNING \
        --variables gof/variables.yaml
fi

# Produce shapes
python shapes/produce_shapes_$ERA.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --gof-channel $CHANNEL \
    --gof-variable $VARIABLE \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR_INCL \
    --era $ERA \
    --tag $ERA \
    --num-threads $NUM_THREADS

# Normalize fake-factor shapes to nominal
python fake-factors/normalize_shifts.py ${ERA}_shapes.root
