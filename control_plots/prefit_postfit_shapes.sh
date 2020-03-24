#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh

# Prefit shapes
logandrun PostFitShapesFromWorkspace -m 125 -w output/workspaces/${ERA}-${CHANNEL}-${VARIABLE}-control-workspace.root \
    -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-control/cmb/125/combined.txt.cmb -o output/shapes/${ERA}-${CHANNEL}-${VARIABLE}-control-datacard-shapes-prefit.root
