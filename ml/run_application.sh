#!/bin/bash

CHANNEL=$1

ARTUS_OUTPUTS=/storage/c/wunsch/Artus_2017-11-17/classified
KAPPA_DATABASE=/portal/ekpbms1/home/wunsch/CMSSW_7_4_7/src/Kappa/Skimming/data/datasets.json

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python ml/write_application_filelist.py \
    --directory $ARTUS_OUTPUTS \
    --database $KAPPA_DATABASE \
    --channel ${CHANNEL} \
    --output ml/${CHANNEL}/application_filelist.yaml

export KERAS_BACKEND=theano
export OMP_NUM_THREADS=4
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

python ml/run_application.py \
    --dataset-config ml/${CHANNEL}/dataset_config.yaml \
    --training-config ml/${CHANNEL}_training_config.yaml \
    --application-config ml/${CHANNEL}_keras_application_config.yaml \
    --filelist ml/${CHANNEL}/application_filelist.yaml \
    --num-processes 8
