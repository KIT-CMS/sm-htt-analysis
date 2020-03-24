#!/bin/bash

ERA=$1
CHANNELS=$2
VARIABLE=$3
[[ ! -z $4 ]] && NUM_THREADS=$4 || NUM_THREADS=8
BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions
# NOTE: Binning is committed in this repository.
#./shapes/calculate_binning.sh et
#./shapes/calculate_binning.sh mt
#./shapes/calculate_binning.sh tt
if [[ "$CHANNELS" =~ "em" ]]
then
    PROCESSES=data_obs,EMB,ZTT,ZL,TTL,TTT,VVL,VVT,W,WH125,ZH125,ttH125,ggHWW125,qqHWW125,ggH125,qqH125,WHWW125,ZHWW125,QCD
else
    PROCESSES=data_obs,EMB,ZTT,ZL,TTL,TTT,VVL,VVT,WH125,ZH125,ttH125,ggHWW125,qqHWW125,ggH125,qqH125,WHWW125,ZHWW125,FAKES
fi

# Produce shapes
python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --gof-variable $VARIABLE \
    --processes $PROCESSES \
    --categories control \
    --em-friend-directory $ARTUS_FRIENDS_EM \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --era $ERA \
    --tag ${VARIABLE}-control \
    --num-threads $NUM_THREADS

mv output/shapes/${VARIABLE}-control/${ERA}-${VARIABLE}-control-${CHANNELS}-${PROCESSES}-control-shapes.root output/shapes/${VARIABLE}-control/${ERA}-${VARIABLE}-control-${CHANNELS}-shapes.root
# Normalize fake-factor shapes to nominal
python fake-factor-application/normalize_shifts.py output/shapes/${VARIABLE}-control/${ERA}-${VARIABLE}-control-${CHANNELS}-shapes.root
