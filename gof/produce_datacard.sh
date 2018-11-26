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

# Remove output directory
rm -rf output/${ERA}_smhtt

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
