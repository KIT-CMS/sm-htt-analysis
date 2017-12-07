#!/bin/bash

source utils/setup_cmssw.sh

# Prefit shapes
PostFitShapes -m 125 -d datacard.txt -o datacard_shapes_prefit.root

# Postfit shapes
PostFitShapes -m 125 -d datacard.txt -o datacard_shapes_postfit_sb.root -f mlfit.root:fit_s --postfit
