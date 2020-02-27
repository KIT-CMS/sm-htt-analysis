#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Prefit shapes
PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root \
    -d output/${ERA}_smhtt/cmb/125/combined.txt.cmb -o ${ERA}_datacard_shapes_prefit.root

PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root \
    -d output/${ERA}_smhtt/cmb/125/combined.txt.cmb -o ${ERA}_datacard_shapes_postfit_b.root \
    -f fitDiagnostics.${ERA}.MultiDimFit.mH125.root:fit_b --postfit --sampling 
