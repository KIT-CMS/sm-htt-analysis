#!/bin/bash

ERA=$1
CONFIGKEY=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples_2017.sh

python fake-factors/produce_shapes_2017.py \
        --directory $ARTUS_OUTPUTS \
        --datasets $KAPPA_DATABASE \
        --era $ERA \
        --tag $ERA \
        -c $CONFIGKEY \
        --num-threads 36 # & # NOTE: We are at the file descriptor limit.
