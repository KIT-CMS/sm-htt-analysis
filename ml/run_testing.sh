#!/bin/bash
set -e

era=$1
channel=$2
## is unset && then || else
[[ -z $method ]] && outdir=ml/out/${era}_${SELCHANNEL} ||  outdir=ml/out/${era}_${channel}_${method}

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

# Confusion matrices
TEST_CONFUSION_MATRIX=1
if [ -n "$TEST_CONFUSION_MATRIX" ]; then
logandrun python htt-ml/testing/keras_confusion_matrix.py \
    $outdir/dataset_config.yaml ml/templates/${era}_${channel}_testing.yaml 0

logandrun python htt-ml/testing/keras_confusion_matrix.py \
    $outdir/dataset_config.yaml ml/templates/${era}_${channel}_testing.yaml 1
fi

# Taylor analysis (1D)
export KERAS_BACKEND=tensorflow
TEST_TAYLOR_1D=1
if [ -n "$TEST_TAYLOR_1D" ]; then
logandrun python htt-ml/testing/keras_taylor_1D.py \
    $outdir/dataset_config.yaml ml/templates/${era}_${channel}_testing.yaml 0

logandrun python htt-ml/testing/keras_taylor_1D.py \
    $outdir/dataset_config.yaml ml/templates/${era}_${channel}_testing.yaml 1
fi

# Taylor analysis (ranking)
export KERAS_BACKEND=tensorflow
#TEST_TAYLOR_RANKING=1
if [ -n "$TEST_TAYLOR_RANKING" ]; then
logandrun python htt-ml/testing/keras_taylor_ranking.py \
    $outdir/dataset_config.yaml ml/templates/${era}_${channel}_testing.yaml 0

logandrun python htt-ml/testing/keras_taylor_ranking.py \
    $outdir/dataset_config.yaml ml/templates/${era}_${channel}_testing.yaml 1
fi

# Make plots combining goodness of fit and Taylor ranking
#TEST_PLOT_COMBINED_GOF_TAYLOR=1
if [ -n "$TEST_PLOT_COMBINED_GOF_TAYLOR" ]; then
    for IFOLD in 0 1; do
        logandrun python ml/plot_combined_taylor_gof.py \
            ${era} \
            $outdir/fold${IFOLD}_keras_taylor_ranking.yaml \
            /path/to/gof/result/dir/ \
            ${channel} \
            ${IFOLD} \
            ml/${era}_${channel}/
    done
fi
