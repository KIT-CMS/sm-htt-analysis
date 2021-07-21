#!/bin/bash

ERA=$1
CHANNEL=$2
ANALYSIS_NAME=$3


source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

if [[ $ERA == *"all"* ]]
then
  CONFIGS=output/ml/${ANALYSIS_NAME}/all_eras_${CHANNEL}*/dataset_config.yaml
  logandrun python htt-ml/application/export_keras_to_json.py --config_training ${CONFIGS} --config_application ml/templates/all_eras_application_${CHANNEL}.yaml --conditional 1
else
  CONFIGS=output/ml/${ANALYSIS_NAME}/${ERA}_${CHANNEL}*/dataset_config.yaml
  logandrun python htt-ml/application/export_keras_to_json.py 
fi
