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
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_backgrounds \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 24 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group backgrounds &

# Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_sm_signals \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 4 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group sm_signals &

# Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_nmssm_low \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 6 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group nmssm_low &

# Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_nmssm_high \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 6 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group nmssm_high &

wait

mkdir output/${ERA}_${CHANNELS}_${VARIABLE}/

hadd -f output/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}-${CHANNELS}-shapes.root output/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_sm_signals-${CHANNELS}-shapes.root output/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_backgrounds-${CHANNELS}-shapes.root output/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_nmssm_low-${CHANNELS}-shapes.root output/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_nmssm_high-${CHANNELS}-shapes.root

# Normalize fake-factor shapes to nominal
# logandrun python fake-factor-application/normalize_shifts.py output/shapes/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}-${CHANNELS}-shapes.root
