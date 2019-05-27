#!/bin/bash

ERA=$1
CHANNEL=$2
LOSS=$3

source utils/setup_cvmfs_sft.sh

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought
then
    source utils/setup_cuda.sh
fi


mkdir -p ml/${ERA}_${CHANNEL}

if [[ $LOSS == *"standard"* ]]
then
    python htt-ml/training/keras_training.py ml/${ERA}_${CHANNEL}_training.yaml 0
    python htt-ml/training/keras_training.py ml/${ERA}_${CHANNEL}_training.yaml 1
elif [[ $LOSS == *"custom"* ]]
then
    python htt-ml/training/keras_training_custom_loss.py ml/${ERA}_${CHANNEL}_training_custom_loss.yaml 0
    python htt-ml/training/keras_training_custom_loss.py ml/${ERA}_${CHANNEL}_training_custom_loss.yaml 1
else
    echo "Loss name not implemented, try standard or custom"
fi
