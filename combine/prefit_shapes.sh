#!/bin/bash

source utils/setup_cmssw.sh

# Prefit shapes
PostFitShapes -m 125 -d datacard.txt -o datacard_shapes_prefit.root
