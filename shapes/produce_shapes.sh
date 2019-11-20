#!/bin/bash
set -e
ERA=$1
CHANNELS=$2
TAG=$3
[[ ! -z $4 ]] && PWD=$4 || PWD=$( pwd  )
BINNING=shapes/binning.yaml
cd $PWD

export LCG_RELEASE=95
source utils/setup_cvmfs_sft.sh

source utils/setup_python.sh
source utils/setup_samples.sh $ERA $TAG
source utils/bashFunctionCollection.sh

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
    --tag ${TAG} \
    --channels $CHANNELS \
    --era $ERA \
    --num-threads 10

# Normalize fake-factor shapes to nominal
logandrun python fake-factor-application/normalize_shifts.py output/shapes/${ERA}-${TAG}-${CHANNELS}-shapes.root
