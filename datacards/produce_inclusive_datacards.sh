#!/bin/bash

ERA=$1
VARIABLE=$2
CHANNELS=${@:3}

source utils/setup_cmssw.sh
source utils/setup_python.sh

python datacards/produce_datacard.py --era $ERA --channels $CHANNELS --shapes ${ERA}_shapes.root --gof $VARIABLE --use-data-for-observation
