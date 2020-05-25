#!/bin/bash
set -e
ERA=$1
CHANNELS=$2
VARIABLE=$3
[[ ! -z $4 ]] && PWD=$4 || PWD=$( pwd  )
BINNING=shapes/nmssm_binning.yaml
cd $PWD

export LCG_RELEASE=96
source utils/setup_cvmfs_sft.sh

source utils/setup_python.sh
source utils/setup_samples.sh $ERA $TAG
source utils/bashFunctionCollection.sh
ensureoutdirs

# Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE} \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 42 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $TauTriggers_Friends $NNScore_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends \
    --mt-friend-directory $SVFit_Friends $TauTriggers_Friends $NNScore_Friends \
    --tt-friend-directory $SVFit_Friends $TauTriggers_Friends $NNScore_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR

# Normalize fake-factor shapes to nominal
# logandrun python fake-factor-application/normalize_shifts.py output/shapes/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}-${CHANNELS}-shapes.root
