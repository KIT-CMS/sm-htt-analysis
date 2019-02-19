#!/bin/bash

ERA=2016
CHANNEL=$1
CUT16043=$2
CUT18032=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

python shapes/venn_count.py \
    --cut16043 $CUT16043 \
    --cut18032 $CUT18032 \
    --channel $CHANNEL \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --datasets $KAPPA_DATABASE
