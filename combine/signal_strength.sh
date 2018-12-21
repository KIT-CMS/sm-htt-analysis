#!/bin/bash

ERA=$1
STXS_FIT=$2

source utils/setup_cmssw.sh

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

if [ $STXS_FIT == "inclusive" ]
then
    combine -M MaxLikelihoodFit -m 125 -d ${ERA}_workspace.root \
        --robustFit 1 -n $ERA -v1 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0
    python combine/check_mlfit.py fitDiagnostics${ERA}.root
fi

if [ $STXS_FIT == "stxs_stage0" ] || [ $STXS_FIT == "stxs_stage1" ]
then
    combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace.root \
        --algo singles -t -1 --expectSignal 1 \
        --robustFit 1 -n $ERA -v1 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0
fi
