#!/bin/bash

CHANNEL=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

export KERAS_BACKEND=theano
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought
then
    source utils/setup_cuda.sh
    export KERAS_BACKEND=tensorflow
    export CUDA_VISIBLE_DEVICES='3'
fi

mkdir -p ml/${CHANNEL}

# Confusion matrices
TEST_CONFUSION_MATRIX=1
if [ -n "$TEST_CONFUSION_MATRIX" ]; then
python htt-ml/testing/keras_confusion_matrix.py \
    ml/${CHANNEL}_training_config.yaml ml/${CHANNEL}_keras_testing_config.yaml 0

python htt-ml/testing/keras_confusion_matrix.py \
    ml/${CHANNEL}_training_config.yaml ml/${CHANNEL}_keras_testing_config.yaml 1
fi

# Taylor analysis (1D)
export KERAS_BACKEND=tensorflow
#TEST_TAYLOR_1D=1
if [ -n "$TEST_TAYLOR_1D" ]; then
python htt-ml/testing/keras_taylor_1D.py \
    ml/${CHANNEL}_training_config.yaml ml/${CHANNEL}_keras_testing_config.yaml 0

python htt-ml/testing/keras_taylor_1D.py \
    ml/${CHANNEL}_training_config.yaml ml/${CHANNEL}_keras_testing_config.yaml 1
fi

# Taylor analysis (ranking)
export KERAS_BACKEND=tensorflow
#TEST_TAYLOR_RANKING=1
if [ -n "$TEST_TAYLOR_RANKING" ]; then
python htt-ml/testing/keras_taylor_ranking.py \
    ml/${CHANNEL}_training_config.yaml ml/${CHANNEL}_keras_testing_config.yaml 0

python htt-ml/testing/keras_taylor_ranking.py \
    ml/${CHANNEL}_training_config.yaml ml/${CHANNEL}_keras_testing_config.yaml 1
fi
