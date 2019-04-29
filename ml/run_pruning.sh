#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cvmfs_sft.sh

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought
then
    source utils/setup_cuda.sh
    export KERAS_BACKEND=tensorflow
    export CUDA_VISIBLE_DEVICES='3'
fi


python ml/prune_variables.py \
    ml/${ERA}_${CHANNEL}_training_pruning_0.yaml ${VARIABLE}

python ml/prune_variables.py \
    ml/${ERA}_${CHANNEL}_training_pruning_1.yaml ${VARIABLE}
