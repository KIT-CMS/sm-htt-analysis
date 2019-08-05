#!/bin/bash
renice -n 19 -u `whoami`

ERA=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python recoil_corrections/produce_fit_shapes_${ERA}.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --num-threads 32
