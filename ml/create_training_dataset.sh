#!/bin/bash
set -e 

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

function run_procedure() {
    SELERA=$1
    SELCHANNEL=$2
    source utils/setup_samples.sh $SELERA
    mkdir -p ml/${SELERA}_${SELCHANNEL}

    ARTUS_FRIENDS=""
    if [ ${SELCHANNEL} == 'mt' ]
    then
        ARTUS_FRIENDS=${ARTUS_FRIENDS_MT}
    fi
    if [ ${SELCHANNEL} == 'et' ]
    then
        ARTUS_FRIENDS=${ARTUS_FRIENDS_ET}
    fi
    if [ ${SELCHANNEL} == 'tt' ]
    then
        ARTUS_FRIENDS=${ARTUS_FRIENDS_TT}
    fi
    if [ ${SELCHANNEL} == 'em' ]
    then
        ARTUS_FRIENDS=${ARTUS_FRIENDS_EM}
    fi
    # Write dataset config
    python ml/write_dataset_config.py \
        --era ${SELERA} \
        --channel ${SELCHANNEL} \
        --base-path $ARTUS_OUTPUTS \
        --friend-paths $ARTUS_FRIENDS \
        --database $KAPPA_DATABASE \
        --output-path $PWD/ml/${SELERA}_${SELCHANNEL} \
        --output-filename training_dataset.root \
        --tree-path ${SELCHANNEL}_nominal/ntuple \
        --event-branch event \
        --training-weight-branch training_weight \
        --training-z-estimation-method mc \
        --output-config ml/${SELERA}_${SELCHANNEL}/dataset_config.yaml

    # Create dataset files from config
    ./htt-ml/dataset/create_training_dataset.py ml/${SELERA}_${SELCHANNEL}/dataset_config.yaml

    # Reweight STXS stage 1 signals so that each stage 1 signal is weighted equally but
    # conserve the overall weight of the stage 0 signal
    #python ml/reweight_stxs_stage1.py \
    #    ml/${SELERA}_${SELCHANNEL} \
    #    ml/${SELERA}_${SELCHANNEL}/fold0_training_dataset.root \
    #    ml/${SELERA}_${SELCHANNEL}/fold1_training_dataset.root
}

source utils/multirun.sh
genArgsAndRun run_procedure $@
