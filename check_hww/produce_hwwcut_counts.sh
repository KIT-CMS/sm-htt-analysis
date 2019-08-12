#!/bin/bash
renice -n 19 -u `whoami`

ERA=$1
CHANNELS=${@:2}

BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python check_hww/produce_hwwcut_counts.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --num-threads 32 \
    --channels ${CHANNELS}

#Compute signal loss for predefined new & old cuts
python compute_signal_loss.py
