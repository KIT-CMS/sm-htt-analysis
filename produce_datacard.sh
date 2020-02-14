#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
JETFAKES=$4
EMBEDDING=$5
TAG=$6

STXS_SIGNALS="stxs_stage0"
CATEGORIES="gof"
GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}

rm -rf output/datacards

source utils/setup_cmssw.sh
source utils/setup_python.sh

# Create datacards
$CMSSW_BASE/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy_tauES \
    --base_path=$PWD \
    --input_folder_mt="output/control_shapes" \
    --real_data=true \
    --classic_bbb=true \
    --postfix="-ML" \
    --midfix="-${TAG}-" \
    --auto_rebin=false \
    --rebin_categories=false \
    --stxs_signals=$STXS_SIGNALS \
    --categories="gof" \
    --gof_category_name=$GOF_CATEGORY_NAME \
    --era=$ERA \
    --output="output/datacards"
