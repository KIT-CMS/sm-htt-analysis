#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
CATEGORIES=$3
JETFAKES=$4
EMBEDDING=$5
CHANNELS=${@:6}

NUM_THREADS=8

# Remove output directory
rm -rf output/${ERA}_smhtt

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
