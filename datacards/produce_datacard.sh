#!/bin/bash

TRAINING=$1

source utils/setup_cmssw.sh
source utils/setup_python.sh

python datacards/produce_datacard.py --training $TRAINING
