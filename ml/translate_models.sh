#!/bin/bash

ERA=$1
CHANNEL=$2
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

if [[ -z $3 ]]; then
  TAG="default"
else
  TAG=$3
fi

if [[ $ERA == *"all"* ]]
then
  [[ -z $TAG ]] && outdir=output/ml/all_eras_${CHANNEL} || outdir=output/ml/all_eras_${CHANNEL}_${TAG}
  logandrun python htt-ml/application/export_keras_to_json.py  ${outdir}/dataset_config.yaml ml/templates/all_eras_application_${CHANNEL}.yaml --conditional 1
else
  [[ -z $TAG ]] && outdir=output/ml/${ERA}_${CHANNEL} || outdir=output/ml/${ERA}_${CHANNEL}_${TAG}
  logandrun python htt-ml/application/export_keras_to_json.py ${outdir}/dataset_config.yaml ml/templates/${ERA}_${CHANNEL}_application.yaml
fi
