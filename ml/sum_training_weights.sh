#!/bin/bash
LCG_RELEASE=95
if uname -a | grep ekpdeepthought
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_95/x86_64-ubuntu1804-gcc8-opt/setup.sh
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-ubuntu1604-gcc54-opt/setup.sh
elif uname -a | grep bms1
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-centos7-gcc8-opt/setup.sh
else
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-slc6-gcc8-opt/setup.sh
fi


function run_procedure() {
    SELERA=$1
    SELCHANNEL=$2
    datasetConfFile="ml/${SELERA}_${SELCHANNEL}/dataset_config.yaml"
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
genArgsAndRun run_procedure $@
