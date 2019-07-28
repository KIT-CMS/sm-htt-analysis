#!/bin/bash
set -e 

export LCG_RELEASE=95
if uname -a | grep ekpdeepthought
then
    #source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-ubuntu1604-gcc54-opt/setup.sh
    #source /cvmfs/sft.cern.ch/lcg/views/LCG_95/x86_64-ubuntu1804-gcc8-opt/setup.sh
    echo "Not possible here, use another machine"
    exit 1
fi
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh


method=$3 ##Dont set this var if not needed
if [[ $method == *"emb"* ]]; then
    tauEstimation=emb
else
    tauEstimation=mc
fi
if [[ $method == *"ff"* ]]; then
    jetEstimation=ff
else
    jetEstimation=mc
fi

function run_procedure() {
    SELERA=$1
    SELCHANNEL=$2
    source utils/setup_samples.sh $SELERA
    [[ $method == "" ]] && outdir=$PWD/ml/out/${SELERA}_${SELCHANNEL} ||  outdir=$PWD/ml/out/${SELERA}_${SELCHANNEL}_${method}
    mkdir -p $outdir

    ARTUS_FRIENDS=""
    if [ ${SELCHANNEL} == 'mt' ]
    then
        ARTUS_FRIENDS="${ARTUS_FRIENDS_MT} $FF_Friends_2017"
    fi
    if [ ${SELCHANNEL} == 'et' ]
    then
        ARTUS_FRIENDS="${ARTUS_FRIENDS_ET} $FF_Friends_2017"
    fi
    if [ ${SELCHANNEL} == 'tt' ]
    then
        ARTUS_FRIENDS="${ARTUS_FRIENDS_TT} $FF_Friends_2017"
    fi
    if [ ${SELCHANNEL} == 'em' ]
    then
        ARTUS_FRIENDS=${ARTUS_FRIENDS_EM}
    fi
    # Write dataset config
    (
    set -x
    python ml/write_dataset_config.py \
        --era ${SELERA} \
        --channel ${SELCHANNEL} \
        --base-path $ARTUS_OUTPUTS \
        --friend-paths $ARTUS_FRIENDS \
        --database $KAPPA_DATABASE \
        --output-path $outdir \
        --output-filename training_dataset.root \
        --tree-path ${SELCHANNEL}_nominal/ntuple \
        --event-branch event \
        --training-weight-branch training_weight \
        --training-z-estimation-method $tauEstimation \
        --training-jetfakes-estimation-method $jetEstimation \
        --output-config $outdir/dataset_config.yaml

    # Create dataset files from config
    ./htt-ml/dataset/create_training_dataset.py $outdir/dataset_config.yaml
    )
    # Reweight STXS stage 1 signals so that each stage 1 signal is weighted equally but
    # conserve the overall weight of the stage 0 signal
    #python ml/reweight_stxs_stage1.py \
    #    ml/${SELERA}_${SELCHANNEL} \
    #    ml/${SELERA}_${SELCHANNEL}/fold0_training_dataset.root \
    #    ml/${SELERA}_${SELCHANNEL}/fold1_training_dataset.root
}

source utils/multirun.sh
genArgsAndRun run_procedure $@
