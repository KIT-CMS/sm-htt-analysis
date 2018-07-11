#!/bin/bash

ERA=$1
STXS_FIT=$2

source utils/setup_cmssw.sh

if [ $STXS_FIT == "inclusive" ]
then
    combine -M MaxLikelihoodFit -m 125 ${ERA}_workspace.root \
        --robustFit 1 -n $ERA \
        --minimizerAlgoForMinos=Minuit2,Migrad
fi

if [ $STXS_FIT == 0 ] || [ $STXS_FIT == 1 ]
then
    combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace.root --algo singles \
        --robustFit 1 -n $ERA \
        --minimizerAlgoForMinos=Minuit2,Migrad
fi
