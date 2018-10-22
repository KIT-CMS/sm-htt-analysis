#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
JETFAKES=$4
EMBEDDING=$5

NUM_THREADS=1
STXS_SIGNALS="stxs_stage0"
CATEGORIES="gof"
GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}

source utils/setup_cmssw.sh
source utils/setup_python.sh

#USE_DATACARDPRODUCER=1
if [ -n "$USE_DATACARDPRODUCER" ]; then
python datacards/produce_datacard.py \
    --era $ERA \
    --channels $CHANNEL \
    --gof $VARIABLE \
    --shapes ${ERA}_shapes.root \
    --use-data-for-observation
fi

USE_COMBINEHARVESTER=1
if [ -n "$USE_COMBINEHARVESTER" ]; then
    # Remove output directory
    rm -rf output/ ${ERA}_workspace.root

    # Create datacards
    $CMSSW_BASE/bin/slc6_amd64_gcc491/MorphingSM2017 \
        --base_path=$PWD \
        --input_folder_mt="/" \
        --input_folder_et="/" \
        --input_folder_tt="/" \
        --real_data=true \
        --jetfakes=$JETFAKES \
        --embedding=$EMBEDDING \
        --postfix="-ML" \
        --channel=$CHANNEL \
        --auto_rebin=true \
        --stxs_signals=$STXS_SIGNALS \
        --categories="gof" \
        --gof_category_name=$GOF_CATEGORY_NAME \
        --era=$ERA \
        --output="${ERA}_smhtt"

    # Merge datacards to workspace and define signals to be fitted
    DATACARD_PATH=${PWD}/output/${ERA}_smhtt/cmb/125
    combineTool.py -M T2W -o workspace.root -i ${DATACARD_PATH} --parallel $NUM_THREADS
    cp $DATACARD_PATH/workspace.root ${ERA}_workspace.root
fi
