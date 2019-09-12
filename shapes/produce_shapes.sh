#!/bin/bash
set -e
ERA=$1
CHANNELS=$2
METHOD=$3
BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA
source utils/bashFunctionCollection.sh

if [[ -d output/friend_trees ]]; then
    ARTUS_FRIENDS=output/friend_trees/${ERA}/*/${METHOD}
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS
    ARTUS_FRIENDS_EM=$ARTUS_FRIENDS
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS
fi

# Produce shapes
logandrun python shapes/produce_shapes_$ERA.py \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --train-method ${METHOD} \
    --channels $CHANNELS \
    --era $ERA \
    --num-threads $(recommendCPUs)

# Normalize fake-factor shapes to nominal
logandrun python fake-factor-application/normalize_shifts.py output/shapes/${ERA}-${METHOD}-${CHANNELS}-shapes.root