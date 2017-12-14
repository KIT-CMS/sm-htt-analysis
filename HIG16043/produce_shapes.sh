#!/bin/bash

BINNING=HIG16043/binning.yaml
CHANNELS=$@

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

python HIG16043/calculate_binning_HIG16043.py HIG16043/binning.yaml

python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --HIG16043
