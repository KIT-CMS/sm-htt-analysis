#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Prefit shapes
PostFitShapes -m 125 -d ${ERA}_datacard.txt -o ${ERA}_datacard_shapes_prefit.root
