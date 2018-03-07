#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

python datacards/produce_datacard.py --channels $@