#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cmssw.sh
source utils/setup_python.sh

python datacards/produce_datacard.py \
    --era $ERA \
    --channels $CHANNEL \
    --gof $VARIABLE \
    --shapes ${ERA}_shapes.root \
    --use-data-for-observation
