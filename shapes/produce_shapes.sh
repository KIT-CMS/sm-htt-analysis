#!/bin/bash
set -e

ERA=$1
METHOD=$2
CHANNELS=${@:3}
BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

ARTUS_FRIENDS=$HOME/data/run3/batch-out/${ERA}_${METHOD}/NNScore_workdir/NNScore_collected/
ARTUS_FRIENDS_ET=$ARTUS_FRIENDS
ARTUS_FRIENDS_EM=$ARTUS_FRIENDS
ARTUS_FRIENDS_MT=$ARTUS_FRIENDS
ARTUS_FRIENDS_TT=$ARTUS_FRIENDS
# Produce shapes
(
set -x
python shapes/produce_shapes_$ERA.py \
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
    --tag ${ERA}_${METHOD} \
    --num-threads 32

# Normalize fake-factor shapes to nominal
python fake-factor-application/normalize_shifts.py ${ERA}_${METHOD}_shapes.root
)