#!/bin/bash
set -e
ERA=$1
CHANNEL=$2

source utils/bashFunctionCollection.sh

export KERAS_BACKEND=tensorflow
export OMP_NUM_THREADS=12
export THEANO_FLAGS=gcc.cxxflags=-march=corei7

if uname -a | grep ekpdeepthought; then
    source ~mscham/p/bms3/root-dev/build2/bin/thisroot.sh
    if [[ -z USE_CPU ]]; then
      source utils/setup_cuda.sh
      export PYTHONUSERBASE=$HOME/.local/pylibs-$(hostname)
      export PYTHONPATH=$HOME/.local/pylibs-$(hostname)/lib/python2.7/site-packages:$PYTHONPATH
      export PATH=$HOME/.local/pylibs-$(hostname)/bin:$PATH
    fi
    source utils/setup_cvmfs_sft.sh
else
    source utils/setup_cvmfs_sft.sh
    export PYTHONUSERBASE=$HOME/.local/pylibs-$(hostname)
    export PYTHONPATH=$HOME/.local/pylibs-$(hostname)/lib/python2.7/site-packages:$PYTHONPATH
    export PATH=$HOME/.local/pylibs-$(hostname)/bin:$PATH
fi

if [[ $ERA == *"all"* ]]
then
  outdir=output/ml/all_eras_${CHANNEL}

  mkdir -p $outdir
  logandrun python htt-ml/training/keras_training.py ${outdir}/dataset_config.yaml 0 --balance-batches 1 --conditional 1 #--randomization 1
  logandrun python htt-ml/training/keras_training.py ${outdir}/dataset_config.yaml 1 --balance-batches 1 --conditional 1 #--randomization 1
else
  outdir=output/ml/${ERA}_${CHANNEL}

  mkdir -p $outdir
  logandrun python htt-ml/training/keras_training.py ${outdir}/dataset_config.yaml 0 --balance-batches 1
  logandrun python htt-ml/training/keras_training.py ${outdir}/dataset_config.yaml 1 --balance-batches 1
fi
