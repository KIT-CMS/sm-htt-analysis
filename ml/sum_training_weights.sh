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

CHANNELS=$(if [[ -z $CHANNEL ]]; then echo "tt" "mt" "et"; else echo $CHANNEL; fi)
ERAS=$(if [[ -z $ERA ]]; then echo "2016" "2017"; else echo $ERA; fi)

i=0 ## how many sets of arguments
unset argslist
for era in $ERAS
do
    for channel in $CHANNELS;do
        argslist[$i]=" $era $channel"
        i=$(($i+1))
    done
done

source utils/multirun.sh
multirun run_procedure ${argslist[@]}
