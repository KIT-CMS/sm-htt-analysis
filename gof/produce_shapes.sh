#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
NUM_THREADS=$4
BINNING=gof/${ERA}_${CHANNEL}_binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions if file is not existent
if [ ! -f "$BINNING" ]
then
    python gof/calculate_binning.py \
        --era $ERA \
        --directory $ARTUS_OUTPUTS \
        --em-friend-directories $SVFit_Friends $HHKinFit_Friends \
        --et-friend-directories $SVFit_Friends $HHKinFit_Friends \
        --mt-friend-directories $SVFit_Friends $HHKinFit_Friends \
        --tt-friend-directories $SVFit_Friends $HHKinFit_Friends \
        --datasets $KAPPA_DATABASE \
        --output $BINNING \
        --channel $CHANNEL \
        --variables gof/variables.yaml
fi

if [[ "$CHANNEL" =~ "em" ]]
then
    PROCESSES=data_obs,EMB,ZL,TTL,TTT,VVL,W,ttH125,ggH125,qqH125,QCD
else
    PROCESSES=data_obs,EMB,ZL,TTL,TTT,VVL,ggH125,qqH125,ttH125,FAKES
fi
# Produce shapes
python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNEL \
    --gof-variable $VARIABLE \
    --processes $PROCESSES \
    --categories gof \
    --em-friend-directory $SVFit_Friends $HHKinFit_Friends \
    --et-friend-directory $SVFit_Friends $HHKinFit_Friends \
    --mt-friend-directory $SVFit_Friends $HHKinFit_Friends \
    --tt-friend-directory $SVFit_Friends $HHKinFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --era $ERA \
    --tag $VARIABLE \
    --num-threads $NUM_THREADS

mv output/shapes/${VARIABLE}/${ERA}-${VARIABLE}-${CHANNEL}-${PROCESSES}-gof-shapes.root output/shapes/${VARIABLE}/${ERA}-${VARIABLE}-${CHANNEL}-shapes.root
# Normalize fake-factor shapes to nominal
python fake-factor-application/normalize_shifts.py output/shapes/${VARIABLE}/${ERA}-${VARIABLE}-${CHANNEL}-shapes.root
