#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh

# Prefit shapes
logandrun PostFitShapesFromWorkspace -m 125 -w ${ERA}-${CHANNEL}-${VARIABLE}-workspace.root \
    -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/cmb/125/combined.txt.cmb -o ${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-prefit.root

logandrun PostFitShapesFromWorkspace -m 125 -w ${ERA}-${CHANNEL}-${VARIABLE}-workspace.root \
    -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/cmb/125/combined.txt.cmb -o ${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-postfit-b.root \
    -f fitDiagnostics.${ERA}-${CHANNEL}-${VARIABLE}.MultiDimFit.mH125.root:fit_b --postfit --sampling 
