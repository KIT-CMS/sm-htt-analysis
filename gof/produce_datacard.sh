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
$CMSSW_BASE/bin/slc6_amd64_gcc530/MorphingSM2017 \
    --base_path=$PWD \
    --input_folder_mt="/" \
    --input_folder_et="/" \
    --input_folder_tt="/" \
    --input_folder_em="/" \
    --real_data=true \
    --classic_bbb=false \
    --binomial_bbb=true \
    --jetfakes=$JETFAKES \
    --embedding=$EMBEDDING \
    --postfix="-ML" \
    --channel=$CHANNEL \
    --auto_rebin=false \
    --rebin_categories=false \
    --stxs_signals=$STXS_SIGNALS \
    --categories="gof" \
    --gof_category_name=$GOF_CATEGORY_NAME \
    --era=$ERA \
    --output="${ERA}_smhtt"

# Use Barlow-Beeston-lite approach for bin-by-bin systematics
THIS_PWD=${PWD}
echo $THIS_PWD
cd output/${ERA}_smhtt/cmb/125/
for FILE in *.txt
do
    sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
done
cd $THIS_PWD
