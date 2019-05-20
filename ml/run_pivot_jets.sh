#!/bin/bash

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



#python htt-ml/pivot_adversarial/jet_example_data.py
python htt-ml/pivot_adversarial/tests/jet_example_train.py 10 1234
#python htt-ml/pivot_adversarial/jet_example_ams.py
