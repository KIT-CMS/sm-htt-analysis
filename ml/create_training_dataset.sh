#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

mkdir -p ml/${ERA}_${CHANNEL}

ARTUS_FRIENDS=""
if [ ${CHANNEL} == 'mt' ]
then
    ARTUS_FRIENDS=${ARTUS_FRIENDS_MT}
fi
if [ ${CHANNEL} == 'et' ]
then
    ARTUS_FRIENDS=${ARTUS_FRIENDS_ET}
fi
if [ ${CHANNEL} == 'tt' ]
then
    ARTUS_FRIENDS=${ARTUS_FRIENDS_TT}
fi
if [ ${CHANNEL} == 'em' ]
then
    ARTUS_FRIENDS=${ARTUS_FRIENDS_EM}
fi

# Write dataset config
python ml/write_dataset_config.py \
    --era ${ERA} \
    --channel ${CHANNEL} \
    --base-path $ARTUS_OUTPUTS \
    --friend-paths $ARTUS_FRIENDS \
    --database $KAPPA_DATABASE \
    --output-path $PWD/ml/${ERA}_${CHANNEL} \
    --output-filename training_dataset.root \
    --tree-path ${CHANNEL}_nominal/ntuple \
    --event-branch event \
    --training-weight-branch training_weight \
    --output-config ml/${ERA}_${CHANNEL}/dataset_config.yaml

# Create dataset files from config
./htt-ml/dataset/create_training_dataset.py ml/${ERA}_${CHANNEL}/dataset_config.yaml

# Reweight STXS stage 1 signals so that each stage 1 signal is weighted equally but
# conserve the overall weight of the stage 0 signal
#python ml/reweight_stxs_stage1.py \
#    ml/${ERA}_${CHANNEL} \
#    ml/${ERA}_${CHANNEL}/fold0_training_dataset.root \
#    ml/${ERA}_${CHANNEL}/fold1_training_dataset.root
