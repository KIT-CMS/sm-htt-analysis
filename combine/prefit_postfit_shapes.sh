#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Prefit shapes
# NOTE: The referenced datacard is used for rebinning
PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root \
    -d output/${ERA}_smhtt/cmb/125/combined.txt.cmb -o ${ERA}_datacard_shapes_prefit.root

# Postfit shapes
PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root \
    -d output/${ERA}_smhtt/cmb/125/combined.txt.cmb -o ${ERA}_datacard_shapes_postfit_sb.root -f fitDiagnostics${ERA}.root:fit_s --postfit
