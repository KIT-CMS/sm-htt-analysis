#!/bin/bash
set -e

if uname -a | grep ekpdeepthought
then
  echo "Not possible here, use another machine"
  exit 1
fi

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

ERA=$1
CHANNEL=$2
TAG=$3
tauEstimation=emb
jetEstimation=ff
if [[ $TAG == *"mc_"* ]]; then
  tauEstimation=mc
fi
if [[ $TAG == *"_mc"* ]]; then
  jetEstimation=mc
fi
source utils/setup_samples.sh $ERA $TAG
outdir=output/ml/${ERA}_${CHANNEL}_${TAG}
[[ -d $outdir ]] ||  mkdir -p $outdir

if [ ${CHANNEL} != 'em' ]
then
  FRIENDS="${SVFit_Friends} ${MELA_Friends} ${TauTriggers_Friends} ${FF_Friends}"
else
  FRIENDS="${SVFit_Friends} ${MELA_Friends}"
fi
# Write dataset config
logandrun python ml/write_dataset_config.py \
  --era ${ERA} \
  --channel ${CHANNEL} \
  --base-path $ARTUS_OUTPUTS \
  --friend-paths $FRIENDS \
  --database $KAPPA_DATABASE \
  --output-path $outdir \
  --output-filename training_dataset.root \
  --tree-path ${CHANNEL}_nominal/ntuple \
  --event-branch event \
  --training-weight-branch training_weight \
  --training-z-estimation-method $tauEstimation \
  --training-jetfakes-estimation-method $jetEstimation \
  --output-config $outdir/dataset_config.yaml \
  --training_stxs1p1

# Create dataset files from config
logandrun ./htt-ml/dataset/create_training_dataset.py $outdir/dataset_config.yaml

#  Reweight STXS stage 1 signals so that each stage 1 signal is weighted equally but
#  conserve the overall weight of the stage 0 signal
#  python ml/reweight_stxs_stage1.py \
#     $outdir \
#     $outdir/fold0_training_dataset.root \
#     $outdir/fold1_training_dataset.root

# split the dataset
logandrun hadd -f $outdir/combined_training_dataset.root \
    $outdir/fold0_training_dataset.root \
    $outdir/fold1_training_dataset.root

logandrun python ./ml/sum_training_weights.py \
  --era ${ERA} \
  --channel ${CHANNEL} \
  --dataset $outdir/combined_training_dataset.root \
  --dataset-config-file "$outdir/dataset_config.yaml" \
  --training-template "ml/templates/${ERA}_${CHANNEL}_training.yaml" \
  --channel $CHANNEL \
  --write-weights True
