#!/bin/bash

ERA=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

python fake-factors/produce_shapes.py \
        --directory $ARTUS_OUTPUTS \
        --et-friend-directory $ARTUS_FRIENDS_ET \
        --mt-friend-directory $ARTUS_FRIENDS_MT \
        --tt-friend-directory $ARTUS_FRIENDS_TT \
        --datasets $KAPPA_DATABASE \
        --era $ERA \
        --tag $ERA \
        --num-threads 16 # & # NOTE: We are at the file descriptor limit.