#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_STAGE=$2
CHANNELS=${@:3}

python datacards/produce_datacard.py --era $ERA --channels $CHANNELS --stxs-stage $STXS_STAGE --shapes ${ERA}_shapes.root
