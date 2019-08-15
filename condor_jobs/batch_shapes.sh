#!/bin/bash
PWD=$1
ERA=$2
CHANNELS=${@:3}

cd $PWD
BINNING=shapes/binning.yaml
# ./shapes/produce_shapes.sh $ERA $CHANNELS
source utils/setup_python.sh
source utils/setup_samples.sh $ERA
# Produce shapes
python shapes/produce_shapes_$ERA.py \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --era $ERA \
    --tag ${ERA}_${CHANNELS} \
    --skip-systematic-variations true \
    --num-threads 12

# Normalize fake-factor shapes to nominal
#python fake-factor-application/normalize_shifts.py ${ERA}_shapes.root