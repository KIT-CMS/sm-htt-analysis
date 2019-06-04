#!/bin/bash
renice -n 19 -u `whoami`


ERA=$1

BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python shapes/produce_control_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels mt  \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --num-threads 30

# Produce shapes
python shapes/produce_control_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels et \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --num-threads 30

# Produce shapes
python shapes/produce_control_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels tt \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --num-threads 30

# Produce shapes
python shapes/produce_control_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels em \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --num-threads 30

# Produce shapes
python shapes/produce_control_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels mm \
    --mm-friend-directory $ARTUS_FRIENDS_MM \
    --num-threads 30
