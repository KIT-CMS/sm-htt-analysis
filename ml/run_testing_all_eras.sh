#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought
then
    source utils/setup_cuda.sh
fi

if [[ -z $3 ]]; then
  tag="default"
else
  tag=$3
fi

[[ -z $tag ]] && outdir=output/ml/all_eras_${CHANNEL} ||  outdir=output/ml/all_eras_${CHANNEL}

mkdir -p ${outdir}

# Confusion matrices
TEST_CONFUSION_MATRIX=1
if [ -n "$TEST_CONFUSION_MATRIX" ]; then
logandrun python htt-ml/testing/keras_confusion_matrix.py \
    ${outdir}/dataset_config.yaml ml/templates/all_eras_testing_${CHANNEL}.yaml 0 --era $ERA

logandrun python htt-ml/testing/keras_confusion_matrix.py \
    ${outdir}/dataset_config.yaml ml/templates/all_eras_testing_${CHANNEL}.yaml 1 --era $ERA
fi

# Taylor analysis (1D)
export KERAS_BACKEND=tensorflow
TEST_TAYLOR_1D=1
if [ -n "$TEST_TAYLOR_1D" ]; then
logandrun python htt-ml/testing/keras_taylor_1D.py \
    ${outdir}/dataset_config.yaml ml/templates/all_eras_testing_${CHANNEL}.yaml 0 --era $ERA

logandrun python htt-ml/testing/keras_taylor_1D.py \
    ${outdir}/dataset_config.yaml ml/templates/all_eras_testing_${CHANNEL}.yaml 1 --era $ERA
fi

# Taylor analysis (ranking)
export KERAS_BACKEND=tensorflow
#TEST_TAYLOR_RANKING=1
if [ -n "$TEST_TAYLOR_RANKING" ]; then
logandrun python htt-ml/testing/keras_taylor_ranking.py \
    ${outdir}/dataset_config.yaml ml/templates/all_eras_testing_${CHANNEL}.yaml 0 --era $ERA

logandrun python htt-ml/testing/keras_taylor_ranking.py \
    ${outdir}/dataset_config.yaml ml/templates/all_eras_testing_${CHANNEL}.yaml 1 --era $ERA
fi
