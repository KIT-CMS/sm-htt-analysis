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

#Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_backgrounds \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 12 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group backgrounds &

#Produce shapes
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

#Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_nmssm_low \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 8 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group nmssm_low &

#Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_nmssm_mid \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 8 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group nmssm_mid &

#Produce shapes
logandrun python shapes/produce_nmssm_shapes.py \
    --tag ${ERA}_${CHANNELS}_${VARIABLE}_nmssm_high \
    --era ${ERA} \
    --channels ${CHANNELS} \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --num-threads 8 \
    --directory $ARTUS_OUTPUTS \
    --discriminator-variable $VARIABLE \
    --et-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --em-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $NNScore_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --shape-group nmssm_high &

wait

[ ! -d output/shapes/${ERA}_${CHANNELS}_${VARIABLE} ] && mkdir output/shapes/${ERA}_${CHANNELS}_${VARIABLE}/

hadd -f output/shapes/${ERA}_${CHANNELS}_${VARIABLE}/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}-${CHANNELS}-shapes.root output/shapes/${ERA}_${CHANNELS}_${VARIABLE}_sm_signals/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_sm_signals-${CHANNELS}-shapes.root output/shapes/${ERA}_${CHANNELS}_${VARIABLE}_backgrounds/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_backgrounds-${CHANNELS}-shapes.root output/shapes/${ERA}_${CHANNELS}_${VARIABLE}_nmssm_low/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_nmssm_low-${CHANNELS}-shapes.root output/shapes/${ERA}_${CHANNELS}_${VARIABLE}_nmssm_mid/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_nmssm_mid-${CHANNELS}-shapes.root output/shapes/${ERA}_${CHANNELS}_${VARIABLE}_nmssm_high/${ERA}-${ERA}_${CHANNELS}_${VARIABLE}_nmssm_high-${CHANNELS}-shapes.root

./shapes/normalize_ff_and_sync_shapes.sh $ERA $CHANNELS $VARIABLE

