#!/bin/bash
set -e

BINNING=shapes/binning.yaml

export LCG_RELEASE=95
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
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR

# Normalize fake-factor shapes to nominal
logandrun python fake-factor-application/normalize_shifts.py output/shapes/${TAG}/${ERA}-${TAG}-${CHANNELS}-${PROCESSES}-${CATEGORIES}-shapes.root

# this dirty fix is needed for grid-control to work
mv output/shapes/${TAG}/${ERA}-${TAG}-${CHANNELS}-${PROCESSES}-${CATEGORIES}-shapes.root shape.root
