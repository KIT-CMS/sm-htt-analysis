#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA


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
python check_hww/write_dataset_config.py \
    --era ${ERA} \
    --channel ${CHANNEL} \
    --base-path $ARTUS_OUTPUTS \
    --friend-paths $ARTUS_FRIENDS \
    --database $KAPPA_DATABASE \
    --output-path $PWD/check_hww/${ERA}_${CHANNEL} \
    --output-filename hww_vs_htt.root \
    --tree-path ${CHANNEL}_nominal/ntuple \
    --training-weight-branch training_weight \
    --event-branch event \
    --output-config check_hww/${ERA}_${CHANNEL}/dataset_config.yaml

# Create dataset files from config
./check_hww/create_training_dataset.py check_hww/${ERA}_${CHANNEL}/dataset_config.yaml
