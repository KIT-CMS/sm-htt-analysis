#!/bin/bash

CHANNELS=$@
VARIABLE=m_vis

source utils/setup_cmssw.sh
source utils/setup_python.sh

python datacards/produce_datacard.py --era 2016 --channels $CHANNELS --shapes 2016_shapes.root --gof $VARIABLE --use-data-for-observation

