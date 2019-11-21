#!/bin/bash

ERA=$1
CHANNEL=$2
[[ -z $3 ]] || TAG=$3
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

<<<<<<< HEAD
[[ -z $TAG ]] && outdir=output/ml/${ERA}_${CHANNEL} || outdir=output/ml/${ERA}_${CHANNEL}_${TAG}
logandrun python htt-ml/application/export_keras_to_json.py  ${outdir}/dataset_config.yaml ml/templates/${ERA}_${CHANNEL}_application.yaml
=======
if [[ $ERA == *"all"* ]]
then
  python htt-ml/application/export_keras_to_json.py  ml/all_eras_training_${CHANNEL}.yaml ml/all_eras_application_${CHANNEL}.yaml
else
  python htt-ml/application/export_keras_to_json.py  ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_application.yaml
fi
>>>>>>> Added conditional network setup and implemented switches
