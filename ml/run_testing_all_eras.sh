#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought
then
    source utils/setup_cuda.sh
fi

mkdir -p ml/all_eras_${CHANNEL}

# Confusion matrices
TEST_CONFUSION_MATRIX=1
if [ -n "$TEST_CONFUSION_MATRIX" ]; then
python htt-ml/testing/keras_confusion_matrix.py \
    ml/all_eras_training_${CHANNEL}.yaml ml/all_eras_testing_${CHANNEL}.yaml 0 $ERA

python htt-ml/testing/keras_confusion_matrix.py \
    ml/all_eras_training_${CHANNEL}.yaml ml/all_eras_testing_${CHANNEL}.yaml 1 $ERA
fi

# Taylor analysis (1D)
export KERAS_BACKEND=tensorflow
TEST_TAYLOR_1D=1
if [ -n "$TEST_TAYLOR_1D" ]; then
python htt-ml/testing/keras_taylor_1D.py \
    ml/all_eras_training_${CHANNEL}.yaml ml/all_eras_testing_${CHANNEL}.yaml 0 $ERA

python htt-ml/testing/keras_taylor_1D.py \
    ml/all_eras_training_${CHANNEL}.yaml ml/all_eras_testing_${CHANNEL}.yaml 1 $ERA
fi
