#!/bin/bash
renice -n 19 -u `whoami`


ERA=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce counts
python zpt_reweighting/produce_zptm_reweighting_counts.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --num-threads 30
