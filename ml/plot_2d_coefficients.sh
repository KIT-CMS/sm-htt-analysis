#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=2016
CHANNEL=mt

for FOLD in 0 1
do
    for PROCESS in ggh qqh ztt zll w tt ss misc
    do
        python ml/plot_2d_coefficients.py --era ${ERA} --channel ${CHANNEL} --fold ${FOLD} --process ${PROCESS}
    done
done
