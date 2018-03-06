#!/bin/bash

CHANNEL=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

python ml/write_application_filelist.py \
    --directory $ARTUS_OUTPUTS \
    --database $KAPPA_DATABASE \
    --channel ${CHANNEL} \
    --output ml/${CHANNEL}/application_filelist.yaml

export KERAS_BACKEND=theano
export OMP_NUM_THREADS=1
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

python ml/run_application.py \
    --dataset-config ml/${CHANNEL}/dataset_config.yaml \
    --training-config ml/${CHANNEL}_training_config.yaml \
    --application-config ml/${CHANNEL}_keras_application_config.yaml \
    --filelist ml/${CHANNEL}/application_filelist.yaml \
    --num-processes 12
