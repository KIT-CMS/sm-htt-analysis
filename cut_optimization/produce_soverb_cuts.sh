#!/bin/bash
renice -n 19 -u `whoami`


ERA=$1

BINNING=cut_optimization/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python cut_optimization/produce_soverb_cuts.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels mt et tt em \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --num-threads 20
