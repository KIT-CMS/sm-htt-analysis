#!/bin/bash
set -e
BINNING=shapes/binning.yaml

export LCG_RELEASE=96
source utils/setup_cvmfs_sft.sh

source utils/setup_python.sh
source utils/setup_samples.sh $ERA $TAG
source utils/bashFunctionCollection.sh
ensureoutdirs

# Produce shapes
logandrun python shapes/produce_shapes.py \
    --tag ${TAG} \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --processes ${PROCESSES} \
    --categories ${CATEGORIES} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 1 \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR

# Normalize fake-factor shapes to nominal
logandrun python fake-factor-application/normalize_shifts.py shapes.root
