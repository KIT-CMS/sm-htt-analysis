#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh

# Prefit shapes
logandrun PostFitShapesFromWorkspace -m 125 -w output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-workspace.root \
    -o output/shapes/${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-prefit.root \
    -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/cmb/125/combined.txt.cmb

logandrun PostFitShapesFromWorkspace -m 125 -w output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-workspace.root \
    -o output/shapes/${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-postfit-b.root \
    -f fitDiagnostics.${ERA}-${CHANNEL}-${VARIABLE}.MultiDimFit.mH125.root:fit_b --postfit --sampling \
    -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/cmb/125/combined.txt.cmb
