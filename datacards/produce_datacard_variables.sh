#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

CHANNELS=$1
VARIABLE=$2

python datacards/produce_datacard.py --channels $CHANNELS  --use-data-for-observation --gof $VARIABLE
