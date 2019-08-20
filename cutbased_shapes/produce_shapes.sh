#!/bin/bash

NUMCORES=$1
ERA=$2
VARIABLE=$3
SHAPEGROUP=$4
CHANNEL=$5

BINNING=cutbased_shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python cutbased_shapes/produce_shapes_$ERA.py \
    --directory $ARTUS_OUTPUTS \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNEL \
    --discriminator-variable $VARIABLE \
    --era $ERA \
    --tag ${ERA}_${CHANNEL}_${SHAPEGROUP} \
    --shape-group $SHAPEGROUP \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --num-threads ${NUMCORES}

echo "To normalize fake-factor shapes to nominal, execute the following, after the jobs are ready:"
echo
echo "hadd -f {ERA}_${CHANNEL}_cutbased_shapes_${VARIABLE}.root {ERA}_${CHANNEL}_${SHAPEGROUP}_cutbased_shapes_${VARIABLE}.root"
echo "python fake-factor-application/normalize_shifts.py ${ERA}_${CHANNEL}_cutbased_shapes_${VARIABLE}.root"
