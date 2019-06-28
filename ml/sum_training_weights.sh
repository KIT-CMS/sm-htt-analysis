#!/bin/bash
ERA=$1
CHANNEL=$2


source utils/setup_cvmfs_sft.sh


function run_procedure() {
    SELERA=$1
    SELCHANNEL=$2
    datasetConfFile="ml/${SELERA}_${SELCHANNEL}/dataset_config.yaml"
    ##print commands before executing
    #set -o xtrace

    # for FOLD in 0 1
    # do
    #     python ./ml/sum_training_weights.py \
    #         --era ${SELERA} \
    #         --channel ${SELCHANNEL} \
    #         --dataset ml/${SELERA}_${SELCHANNEL}/fold${FOLD}_training_dataset.root \
    #         --dataset-config-file $datasetConfFile \
    #         --channel $SELCHANNEL \
    #         --write-weights False
    #     echo
    # done
    hadd -f ml/${SELERA}_${SELCHANNEL}/combined_training_dataset.root \
        ml/${SELERA}_${SELCHANNEL}/fold0_training_dataset.root \
        ml/${SELERA}_${SELCHANNEL}/fold1_training_dataset.root

    python ./ml/sum_training_weights.py \
        --era ${SELERA} \
        --channel ${SELCHANNEL} \
        --dataset ml/${SELERA}_${SELCHANNEL}/combined_training_dataset.root \
        --dataset-config-file $datasetConfFile \
        --channel $SELCHANNEL \
         --write-weights True
}


source utils/multirun.sh
genArgsAndRun run_procedure $ERA $CHANNEL 

