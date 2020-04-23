#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cmssw.sh
source utils/setup_python.sh

INPUT=output/shapes/${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-prefit.root

python gof/plot_2d_pulls.py -i $INPUT -e $ERA -c $CHANNEL -v $VARIABLE \
                            -o output/gof/${ERA}-${CHANNEL}-${VARIABLE}/${ERA}_plots/

INPUT=output/shapes/${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-postfit-b.root
python gof/plot_2d_pulls.py -i $INPUT -e $ERA -c $CHANNEL -v $VARIABLE \
                            -o output/gof/${ERA}-${CHANNEL}-${VARIABLE}/${ERA}_plots/ \
                            --postfit
