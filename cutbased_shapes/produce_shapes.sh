#!/bin/bash
renice -n 19 -u `whoami`

BINNING=cutbased_shapes/binning.yaml
ERA=$1
VARIABLE=$2
SHAPEGROUP=$3
CHANNELS=${@:4}

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python cutbased_shapes/produce_shapes_$ERA.py \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --discriminator-variable $VARIABLE \
    --era $ERA \
    --tag ${ERA}_${CHANNELS}_${SHAPEGROUP} \
    --shape-group $SHAPEGROUP \
    --num-threads 20

# Normalize fake-factor shapes to nominal
python fake-factor-application/normalize_shifts.py ${ERA}_${CHANNELS}_${SHAPEGROUP}_cutbased_shapes_${VARIABLE}.root
