#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
CHANNEL=$2

for FOLD in 0 1
do
    for PROCESS in ggh qqh
    do
        python ml/plot_2d_coefficients.py --era ${ERA} --channel ${CHANNEL} --fold ${FOLD} --process ${PROCESS}
    done
done
