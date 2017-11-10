#!/bin/bash

CHANNEL=$1
VARIABLE=$2

./combine/prefit_postfit_shapes.sh

source utils/setup_cmssw.sh

./plotting/plot_shapes.py -i datacard_shapes_prefit.root -f ${CHANNEL}_${VARIABLE}_prefit
./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -f ${CHANNEL}_${VARIABLE}_postfit
