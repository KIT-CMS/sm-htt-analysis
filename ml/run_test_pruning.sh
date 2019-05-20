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
    export KERAS_BACKEND=tensorflow
    export CUDA_VISIBLE_DEVICES='3'
fi

mkdir -p ml/${ERA}_${CHANNEL}

# Put recall and precision scores into .json file. Usage for variable pruning. Plotting with plot_recall_precision!
TEST_RECALL_PRECISION=1
if [ -n "$TEST_RECALL_PRECISION" ]; then
python htt-ml/testing/keras_recall_precision.py \
    ml/${ERA}_${CHANNEL}_training_pruning_0.yaml ml/${ERA}_${CHANNEL}_testing.yaml 0

python htt-ml/testing/keras_recall_precision.py \
    ml/${ERA}_${CHANNEL}_training_pruning_1.yaml ml/${ERA}_${CHANNEL}_testing.yaml 1
fi

# Confusion matrices
TEST_CONFUSION_MATRIX=1
if [ -n "$TEST_CONFUSION_MATRIX" ]; then
python htt-ml/testing/keras_confusion_matrix.py \
    ml/${ERA}_${CHANNEL}_training_pruning_0.yaml ml/${ERA}_${CHANNEL}_testing.yaml 0

python htt-ml/testing/keras_confusion_matrix.py \
    ml/${ERA}_${CHANNEL}_training_pruning_1.yaml ml/${ERA}_${CHANNEL}_testing.yaml 1
fi