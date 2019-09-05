#!/bin/bash
set -e
ERA=$1
CHANNEL=$2

source utils/bashFunctionCollection.sh
# source /cvmfs/sft.cern.ch/lcg/views/LCG_95apython3/x86_64-ubuntu1604-gcc54-opt/setup.sh

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought ; then
    source ~mscham/p/bms3/root-dev/build2/bin/thisroot.sh
    source utils/setup_cuda.sh
    export PYTHONUSERBASE=$HOME/.local/pylibs-$(hostname)
    export PYTHONPATH=$HOME/.local/pylibs-$(hostname)/lib/python2.7/site-packages:$PYTHONPATH
    export PATH=$HOME/.local/pylibs-$(hostname)/bin:$PATH
else
    source utils/setup_cvmfs_sft.sh
    export PYTHONUSERBASE=$HOME/.local/pylibs-$(hostname)
    export PYTHONPATH=$HOME/.local/pylibs-$(hostname)/lib/python2.7/site-packages:$PYTHONPATH
    export PATH=$HOME/.local/pylibs-$(hostname)/bin:$PATH
fi


[[ -z $method ]] && outdir=ml/out/${ERA}_${CHANNEL} || outdir=ml/out/${ERA}_${CHANNEL}_${method}

mkdir -p $outdir

logandrun python htt-ml/training/keras_training.py $outdir/dataset_config.yaml 0 --balance-batches True
logandrun python htt-ml/training/keras_training.py $outdir/dataset_config.yaml 1 --balance-batches True
