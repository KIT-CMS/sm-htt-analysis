#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
STXS_CATEGORIES=$3
CHANNELS=${@:4}

python datacards/produce_datacard.py \
    --era $ERA \
    --channels $CHANNELS \
    --stxs-signals $STXS_SIGNALS \
    --stxs-categories $STXS_CATEGORIES \
    --shapes ${ERA}_shapes.root
