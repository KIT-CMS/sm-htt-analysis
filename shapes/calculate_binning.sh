#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ARTUS_OUTPUTS=$1
KAPPA_DATABASE=$2

python shapes/calculate_binning.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --percentiles 0 20 40 60 80 100 \
    --output shapes/binning.yaml \
     --et-training keras1 \
     --mt-training keras13
