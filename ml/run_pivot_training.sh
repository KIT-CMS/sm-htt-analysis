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


#python htt-ml/pivot_adversarial/pivot_create_toy_dataset.py ml/pivot_toy_training.yaml
#python htt-ml/pivot_adversarial/pivot_train.py ml/pivot_toy_training.yaml False 0

python htt-ml/pivot_adversarial/pivot_train_real.py ml/pivot_adversarial_training.yaml 0
python htt-ml/pivot_adversarial/pivot_train_real.py ml/pivot_adversarial_training.yaml 1
