#!/bin/bash

ERA=$1
CHANNEL=$2
ANALYSIS_NAME=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

if [[ $ERA == *"all"* ]]
then
  outdir=output/ml/${ANALYSIS_NAME}/all_eras_${CHANNEL}
  logandrun python htt-ml/application/export_keras_to_json.py  ${outdir}/dataset_config.yaml ml/templates/all_eras_application_${CHANNEL}.yaml --conditional 1
else
  outdir=output/ml/${ANALYSIS_NAME}/${ERA}_${CHANNEL}
  logandrun python htt-ml/application/export_keras_to_json.py ${outdir}/dataset_config.yaml ml/templates/${ERA}_${CHANNEL}_application.yaml
fi
