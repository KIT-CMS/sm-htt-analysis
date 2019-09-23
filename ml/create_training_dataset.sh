#!/bin/bash
set -e

if uname -a | grep ekpdeepthought
then
    #source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-ubuntu1604-gcc54-opt/setup.sh
    #source /cvmfs/sft.cern.ch/lcg/views/LCG_95/x86_64-ubuntu1804-gcc8-opt/setup.sh
    echo "Not possible here, use another machine"
    exit 1
fi
LCG_RELEASE=95
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

function run_procedure() {
    ERA=$1
    CHANNEL=$2
    METHOD=$3

    tauEstimation=emb
    jetEstimation=ff
    if [[ $METHOD == *"mc_"* ]]; then
        tauEstimation=mc
    fi
    if [[ $METHOD == *"_mc"* ]]; then
        jetEstimation=mc
    fi

    source utils/setup_samples.sh $ERA
    [[ -z $METHOD ]] && outdir=ml/out/${ERA}_${CHANNEL} ||  outdir=ml/out/${ERA}_${CHANNEL}_${METHOD}
    mkdir -p $outdir

    ARTUS_FRIENDS=""
    if [ ${CHANNEL} == 'mt' ]
    then
        ARTUS_FRIENDS="${ARTUS_FRIENDS_MT} $FF_Friends_2017"
    fi
    if [ ${CHANNEL} == 'et' ]
    then
        ARTUS_FRIENDS="${ARTUS_FRIENDS_ET} $FF_Friends_2017"
    fi
    if [ ${CHANNEL} == 'tt' ]
    then
        ARTUS_FRIENDS="${ARTUS_FRIENDS_TT} $FF_Friends_2017"
    fi
    if [ ${CHANNEL} == 'em' ]
    then
        ARTUS_FRIENDS=${ARTUS_FRIENDS_EM}
    fi
    # Write dataset config
     logandrun python ml/write_dataset_config.py \
         --era ${ERA} \
         --channel ${CHANNEL} \
         --base-path $ARTUS_OUTPUTS \
         --friend-paths $ARTUS_FRIENDS \
         --database $KAPPA_DATABASE \
         --output-path $outdir \
         --output-filename training_dataset.root \
         --tree-path ${CHANNEL}_nominal/ntuple \
         --event-branch event \
         --training-weight-branch training_weight \
         --training-z-estimation-method $tauEstimation \
         --training-jetfakes-estimation-method $jetEstimation \
         --output-config $outdir/dataset_config.yaml

     # # Create dataset files from config
     logandrun ./htt-ml/dataset/create_training_dataset.py $outdir/dataset_config.yaml
     # Reweight STXS stage 1 signals so that each stage 1 signal is weighted equally but
     # conserve the overall weight of the stage 0 signal
     #python ml/reweight_stxs_stage1.py \
     #    $outdir \
     #    $outdir/fold0_training_dataset.root \
     #    $outdir/fold1_training_dataset.root
     # split the dataset
     logandrun hadd -f $outdir/combined_training_dataset.root \
         $outdir/fold0_training_dataset.root \
         $outdir/fold1_training_dataset.root

    # write the classweight to dataset_config.yaml
    logandrun python ./ml/yamlmerge.py \
        --era ${ERA} \
        --channel ${CHANNEL} \
        --dataset-config-file ml/out/${ERA}_${CHANNEL}_${METHOD}/dataset_config.yaml
}
IFS=',' read -r -a eras <<< $1
IFS=',' read -r -a channels <<< $2
IFS=',' read -r -a methods <<< $3

for method in ${methods[@]}; do
    for era in ${eras[@]}; do
        for channel in ${channels[@]}; do
            run_procedure $era $channel $method
        done
    done
done