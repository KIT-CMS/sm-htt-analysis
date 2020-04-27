#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

ID=${ERA}-${CHANNEL}-${VARIABLE}

source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh

# Prefit shapes
logandrun PostFitShapesFromWorkspace -m 125 -w output/datacards/${ID}-smhtt-gof/${ID}-workspace.root \
    -o output/shapes/${ID}-datacard-shapes-prefit.root \
    -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/cmb/125/combined.txt.cmb

logandrun PostFitShapesFromWorkspace -m 125 -w output/datacards/${ID}-smhtt-gof/${ID}-workspace.root \
    -o output/shapes/${ID}-datacard-shapes-postfit-b.root \
    -f output/datacards/${ID}-smhtt-gof/fitDiagnostics.${ID}.MultiDimFit.mH125.root:fit_b --postfit --sampling \
    -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/cmb/125/combined.txt.cmb
