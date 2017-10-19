#!/bin/bash

CHANNEL="mt"

export KERAS_BACKEND=theano
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

python htt-ml/training/TMVA_training.py ml/${CHANNEL}_training_config.yaml 0
python htt-ml/training/TMVA_training.py ml/${CHANNEL}_training_config.yaml 1
