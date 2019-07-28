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

method=$3 ##Dont set this var if not needed

function run_procedure() {
    SELERA=$1
    SELCHANNEL=$2
    [[ $method == "" ]] && outdir=ml/out/${SELERA}_${SELCHANNEL} ||  outdir=ml/out/${SELERA}_${SELCHANNEL}_${method}

    hadd -f $outdir/combined_training_dataset.root \
        $outdir/fold0_training_dataset.root \
        $outdir/fold1_training_dataset.root

    python ./ml/sum_training_weights.py \
        --era ${SELERA} \
        --channel ${SELCHANNEL} \
        --dataset $outdir/combined_training_dataset.root \
        --dataset-config-file "$outdir/dataset_config.yaml" \
        --channel $SELCHANNEL \
         --write-weights True
}

source utils/multirun.sh
genArgsAndRun run_procedure $@
