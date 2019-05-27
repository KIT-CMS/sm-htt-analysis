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

# Draw recall and precision scores from .json file. Usage for variable pruning
TEST_RECALL_PRECISION=1
if [ -n "$TEST_RECALL_PRECISION" ]; then
python htt-ml/testing/keras_recall_precision.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 0

python htt-ml/testing/keras_recall_precision.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 1
fi

# Confusion matrices
TEST_CONFUSION_MATRIX=1
if [ -n "$TEST_CONFUSION_MATRIX" ]; then
python htt-ml/testing/keras_confusion_matrix.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 0

python htt-ml/testing/keras_confusion_matrix.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 1
fi

# Signifance on test data
TEST_SIGNIFICANCE=1
if [ -n "$TEST_SIGNIFICANCE" ]; then
python htt-ml/testing/keras_significance.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 0

python htt-ml/testing/keras_significance.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 1
fi

# Taylor analysis (1D)
export KERAS_BACKEND=tensorflow
#TEST_TAYLOR_1D=1
if [ -n "$TEST_TAYLOR_1D" ]; then
python htt-ml/testing/keras_taylor_1D.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 0

python htt-ml/testing/keras_taylor_1D.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 1
fi

# Taylor analysis (ranking)
export KERAS_BACKEND=tensorflow
#TEST_TAYLOR_RANKING=1
if [ -n "$TEST_TAYLOR_RANKING" ]; then
python htt-ml/testing/keras_taylor_ranking.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 0

python htt-ml/testing/keras_taylor_ranking.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_testing.yaml 1
fi

# Make plots combining goodness of fit and Taylor ranking
#TEST_PLOT_COMBINED_GOF_TAYLOR=0
if [ -n "$TEST_PLOT_COMBINED_GOF_TAYLOR" ]; then
    for IFOLD in 0 1; do
        python ml/plot_combined_taylor_gof.py \
            ${ERA} \
            ml/${ERA}_${CHANNEL}/fold${IFOLD}_keras_taylor_ranking.yaml \
            /path/to/gof/result/dir/ \
            ${CHANNEL} \
            ${IFOLD} \
            ml/${ERA}_${CHANNEL}/
    done
fi