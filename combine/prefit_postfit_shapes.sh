#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Prefit shapes
PostFitShapes -m 125 -d ${ERA}_datacard.txt -o ${ERA}_datacard_shapes_prefit.root

# Postfit shapes
PostFitShapes -m 125 -d ${ERA}_datacard.txt -o ${ERA}_datacard_shapes_postfit_sb.root -f mlfit${ERA}.root:fit_s --postfit
PostFitShapes -m 125 -d ${ERA}_datacard.txt -o ${ERA}_datacard_shapes_postfit_b.root -f mlfit${ERA}.root:fit_b --postfit
