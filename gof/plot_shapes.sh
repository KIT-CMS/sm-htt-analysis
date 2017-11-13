#!/bin/bash

CHANNEL=$1
VARIABLE=$2

source utils/setup_cmssw.sh

PostFitShapes -m 125 -d datacard.txt -o datacard_shapes_prefit.root
./plotting/plot_shapes.py -i datacard_shapes_prefit.root -f ${CHANNEL}_${VARIABLE}_prefit
