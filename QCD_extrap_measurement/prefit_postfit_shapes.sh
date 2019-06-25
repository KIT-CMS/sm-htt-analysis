#!/bin/bash
ERA=$1
source utils/setup_cmssw.sh

# Prefit shapes
#PostFitShapes -m 125 -d ${ERA}_workspace.root -o datacard_shapes_prefit.root

# Postfit shapes
#PostFitShapes -m 125 -d ${ERA}_workspace.root -o datacard_shapes_postfit_sb.root -f mlfit.root:fit_s --postfit

PostFitShapesFromWorkspace -w "${ERA}"_workspace.root -m 125 -o "${ERA}"_datacard_shapes_prefit.root -d output/"${ERA}"_smhtt/cmb/125/combined.txt.cmb --print --postfit -f fitDiagnostics"${ERA}".root:fit_s
