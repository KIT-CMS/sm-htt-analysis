#!/bin/bash
set -e
ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought ; then
    source utils/setup_cuda.sh
fi
export PYTHONUSERBASE=$HOME/.local/pylibs-$(hostname)
export PYTHONPATH=$HOME/.local/pylibs-$(hostname)/lib/python2.7/site-packages:$PYTHONPATH
export PATH=$HOME/.local/pylibs-$(hostname)/bin:$PATH

method=$3
[[ $method == "" ]] && outdir=$PWD/ml/out/${ERA}_${CHANNEL} ||  outdir=$PWD/ml/out/${ERA}_${CHANNEL}_${method}

mkdir -p $outdir

(
set -x
python htt-ml/training/keras_training.py $outdir/dataset_config.yaml 0
python htt-ml/training/keras_training.py $outdir/dataset_config.yaml 1
)