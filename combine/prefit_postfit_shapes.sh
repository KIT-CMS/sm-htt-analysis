#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Prefit shapes
PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root -o ${ERA}_datacard_shapes_prefit.root

# Postfit shapes
PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root -o ${ERA}_datacard_shapes_postfit_sb.root -f mlfit${ERA}.root:fit_s --postfit
PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root -o ${ERA}_datacard_shapes_postfit_b.root -f mlfit${ERA}.root:fit_b --postfit
