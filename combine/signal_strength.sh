#!/bin/bash

ERA=$1
STXS_FIT=$2

source utils/setup_cmssw.sh

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

if [ $STXS_FIT == "robustHesse" ]
then
    combine -M MaxLikelihoodFit -m 125 -d ${ERA}_workspace.root \
        --robustFit 1 -n $ERA -v1 \
        --robustHesse 1 \
        -t -1 --expectSignal 1 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0
    #python combine/check_mlfit.py fitDiagnostics${ERA}.root
    root -l fitDiagnostics${ERA}.root <<< "fit_b->Print(); fit_s->Print()" | grep "covariance matrix quality"
fi

if [ $STXS_FIT == "inclusive" ] || [ $STXS_FIT == "stxs_stage0" ] || [ $STXS_FIT == "stxs_stage1p1" ]
then
    combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace.root \
        --algo singles --robustFit 1 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --floatOtherPOIs 1 \
        -t -1 --expectSignal 1 \
        -n $ERA -v1
    python combine/print_fitresult.py higgsCombine${ERA}.MultiDimFit.mH125.root
fi
