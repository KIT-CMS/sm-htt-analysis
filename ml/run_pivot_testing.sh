#!/bin/bash

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

# Draw recall and precision scores from .json file. Usage for variable pruning
#TEST_TOY=1
if [ -n "$TEST_TOY" ]; then
python htt-ml/pivot_adversarial/pivot_plot_toy.py \
    ml/pivot_toy_training.yaml ml/pivot_toy_testing.yaml 0

fi
TEST_REAL=1
if [ -n "$TEST_REAL" ]; then
python htt-ml/pivot_adversarial/pivot_plot_significance.py \
    ml/pivot_adversarial_training.yaml ml/pivot_adversarial_testing.yaml 0

fi