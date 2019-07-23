#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

if uname -a | grep ekpdeepthought
then
    source utils/setup_cuda.sh
fi

python ml/write_application_filelist.py \
    --directory $ARTUS_OUTPUTS \
    --database $KAPPA_DATABASE \
    --channel ${CHANNEL} \
    --era ${ERA} \
    --output ml/${ERA}_${CHANNEL}/application_filelist.yaml

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=1
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

python ml/run_application.py \
    --dataset-config ml/${ERA}_${CHANNEL}/dataset_config.yaml \
    --training-config ml/${ERA}_${CHANNEL}_training.yaml \
    --application-config ml/${ERA}_${CHANNEL}_application.yaml \
    --filelist ml/${ERA}_${CHANNEL}/application_filelist.yaml \
    --num-processes 10
