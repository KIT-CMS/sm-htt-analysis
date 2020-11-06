#!/bin/bash

ERA=$1
CHANNEL=$2
TAG=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

if [[ $ERA == *"all"* ]]
then
  outdir=output/ml/all_eras_${CHANNEL}_${TAG} 
  logandrun python htt-ml/application/export_keras_to_json.py  ${outdir}/dataset_config.yaml ml/templates/all_eras_application_${CHANNEL}.yaml --conditional 1
else
  outdir=output/ml/${ERA}_${CHANNEL}_${TAG}
  logandrun python htt-ml/application/export_keras_to_json.py ${outdir}/dataset_config.yaml ml/templates/${ERA}_${CHANNEL}_application.yaml
fi
