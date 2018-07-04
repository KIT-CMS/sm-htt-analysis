#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
STXS_CATEGORIES=$3
CHANNELS=${@:4}

#USE_DATACARDPRODUCER=1
if [ -n "$USE_DATACARDPRODUCER" ]; then
    python datacards/produce_datacard.py \
        --era $ERA \
        --channels $CHANNELS \
        --stxs-signals $STXS_SIGNALS \
        --stxs-categories $STXS_CATEGORIES \
        --shapes ${ERA}_shapes.root
fi

USE_COMBINEHARVESTER=1
if [ -n "$USE_COMBINEHARVESTER" ]; then
    CMSSW_7_4_7/bin/slc6_amd64_gcc491/MorphingSM2017 \
        --input_folder_mt="../../../../.." \
        --real_data=false \
        --jetfakes=false \
        --postfix="-ML" \
        --channel="mt" \
        --auto_rebin=true \
        --output="smhtt"

    combineTool.py -M T2W -o workspace.root -i output/smhtt/cmb/125/*.txt --parallel 8
fi
