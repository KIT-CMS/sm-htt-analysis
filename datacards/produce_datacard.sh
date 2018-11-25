#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
CATEGORIES=$3
STXS_FIT=$4
JETFAKES=$5
EMBEDDING=$6
CHANNELS=${@:7}

NUM_THREADS=8

#USE_DATACARDPRODUCER=1
if [ -n "$USE_DATACARDPRODUCER" ]; then
    python datacards/produce_datacard.py \
        --era $ERA \
        --channels $CHANNELS \
        --stxs-signals $STXS_SIGNALS \
        --stxs-categories $CATEGORIES \
        --shapes ${ERA}_shapes.root

    combineTool.py -M T2W -o ${ERA}_workspace.root -i ${ERA}_datacard.txt -m 125.0 --parallel $NUM_THREADS
fi

USE_COMBINEHARVESTER=1
if [ -n "$USE_COMBINEHARVESTER" ]; then
    # Remove output directory
    rm -rf output/${ERA}_output ${ERA}_workspace.root

    # Create datacards
    $CMSSW_BASE/bin/slc6_amd64_gcc491/MorphingSM2017 \
        --base_path=$PWD \
        --input_folder_mt="/" \
        --input_folder_et="/" \
        --input_folder_tt="/" \
        --real_data=false \
        --jetfakes=$JETFAKES \
        --embedding=$EMBEDDING \
        --postfix="-ML" \
        --channel="${CHANNELS}" \
        --auto_rebin=true \
        --stxs_signals=$STXS_SIGNALS \
        --categories=$CATEGORIES \
        --era=$ERA \
        --output="${ERA}_smhtt"
fi
