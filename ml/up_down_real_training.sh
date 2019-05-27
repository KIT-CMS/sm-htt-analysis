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


#python htt-ml/up_down_shift_loss/create_dataset.py ml/up_down_real_training.yaml 0
#python htt-ml/up_down_shift_loss/create_dataset.py ml/up_down_real_training.yaml 1
python htt-ml/up_down_shift_loss/train.py ml/up_down_real_training.yaml 0
python htt-ml/up_down_shift_loss/train.py ml/up_down_real_training.yaml 1
python htt-ml/up_down_shift_loss/test.py ml/up_down_real_training.yaml 0
python htt-ml/up_down_shift_loss/test.py ml/up_down_real_training.yaml 1

