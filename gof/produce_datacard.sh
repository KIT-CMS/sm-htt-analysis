#!/bin/bash

CHANNEL=$1
VARIABLE=$2

source utils/setup_cmssw.sh
source utils/setup_python.sh

python datacards/produce_datacard.py --channels $CHANNEL --gof $VARIABLE --use-data-for-observation --emb
