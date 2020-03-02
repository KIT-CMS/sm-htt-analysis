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

source utils/setup_cmssw.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

OUTPUTDIR="output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof"

# Remove output directory
[[ ! -d $OUTPUTDIR ]] || rm -r $OUTPUTDIR

# Create datacards
logandrun ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
    --base_path=$PWD \
    --input_folder_mt="output/shapes" \
    --input_folder_et="output/shapes" \
    --input_folder_tt="output/shapes" \
    --input_folder_em="output/shapes" \
    --real_data=true \
    --classic_bbb=false \
    --binomial_bbb=true \
    --jetfakes=$JETFAKES \
    --embedding=$EMBEDDING \
    --ggh_wg1=false \
    --qqh_wg1=false \
    --postfix="-ML" \
    --midfix="-${TAG}-" \
    --channel=$CHANNEL \
    --auto_rebin=false \
    --rebin_categories=false \
    --stxs_signals=$STXS_SIGNALS \
    --categories="gof" \
    --gof_category_name=$GOF_CATEGORY_NAME \
    --era=$ERA \
    --output=${OUTPUTDIR} | tee output/log/datacard-gof-${ERA}-${CHANNEL}-${VARIABLE}-${JETFAKES}-${EMBEDDING}.log

# Use Barlow-Beeston-lite approach for bin-by-bin systematics
pushd ${OUTPUTDIR}/cmb/125/
for FILE in *.txt
do
    sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
done
popd
