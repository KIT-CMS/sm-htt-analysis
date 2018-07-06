#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
STXS_CATEGORIES=$3
CHANNELS=${@:4}

USE_DATACARDPRODUCER=1
if [ -n "$USE_DATACARDPRODUCER" ]; then
    python datacards/produce_datacard.py \
        --era $ERA \
        --channels $CHANNELS \
        --stxs-signals $STXS_SIGNALS \
        --stxs-categories $STXS_CATEGORIES \
        --shapes ${ERA}_shapes.root

    combineTool.py -M T2W -o ${ERA}_workspace.root -i ${ERA}_datacard.txt -m 125.0 --parallel 8
fi

#USE_COMBINEHARVESTER=1
if [ -n "$USE_COMBINEHARVESTER" ]; then
    CMSSW_7_4_7/bin/slc6_amd64_gcc491/MorphingSM2017 \
        --input_folder_mt="../../../../.." \
        --input_folder_et="../../../../.." \
        --input_folder_tt="../../../../.." \
        --real_data=false \
        --jetfakes=false \
        --postfix="-ML" \
        --channel="${CHANNELS}" \
        --auto_rebin=true \
        --output="${ERA}_smhtt"

    DATACARD_PATH=output/${ERA}_smhtt/cmb/125
    combineTool.py -M T2W -o workspace.root -i ${DATACARD_PATH} --parallel 8
    cp $DATACARD_PATH/workspace.root ${ERA}_workspace.root
fi
