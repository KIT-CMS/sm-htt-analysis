#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Prefit shapes
PostFitShapesFromWorkspace -m 125 -w ${ERA}_workspace.root -o ${ERA}_datacard_shapes_prefit.root
