#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

CHANNELS=$1
VARIABLE=$2

if [ -z $VARIABLE ]; then
python datacards/produce_datacard.py --channels $CHANNELS --emb --use-data-for-observation
else
python datacards/produce_datacard.py --channels $CHANNELS  --emb --use-data-for-observation --gof $VARIABLE
fi
