#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

combine -M ChannelCompatibilityCheck -d ${PWD}/${ERA}_workspace.root -m 125.0 -n ${ERA} \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        --robustFit 1 \
        --X-rtd FITTER_NEW_CROSSING_ALGO \
        -v 1 \
        --group htt_em \
        --group htt_et \
        --group htt_mt \
        --group htt_tt \
        --rMin -1 --rMax 3 \
        --saveFitResult
