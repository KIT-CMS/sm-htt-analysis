#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
CHANNELS=${@:2}

python datacards/produce_datacard.py --era $ERA --channels $CHANNELS
