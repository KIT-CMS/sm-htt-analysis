#!/bin/bash
set -e

trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

source utils/setup_cmssw.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

ERA=$1
STXS_SIGNALS=$2
CATEGORIES=$3
JETFAKES=$4
EMBEDDING=$5
TAG=$6
CHANNELS=$7
NUM_THREADS=8

TRAIN_EMB=1
TRAIN_FF=1
if [[ $TAG == *"mc_"* ]]; then
    TRAIN_EMB=0
fi
if [[ $TAG == *"_mc"* ]]; then
    TRAIN_FF=0
fi
TRAIN_STAGE0=0
if [[ $TAG == *"stage0"* ]]; then
    TRAIN_STAGE0=1
fi
OUTPUTDIR="output/datacards/${ERA}-${TAG}-smhtt-ML/${STXS_SIGNALS}"

# Remove output directory
[[ ! -d $OUTPUTDIR ]] || rm -r $OUTPUTDIR

trap 'exit $?' TRAP KILL EXIT

# Create datacards
logandrun ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
    --base_path=$PWD \
    --input_folder_mt="output/shapes" \
    --input_folder_et="output/shapes" \
    --input_folder_tt="output/shapes" \
    --input_folder_em="output/shapes" \
    --real_data=false \
    --classic_bbb=false \
    --binomial_bbb=true \
    --jetfakes=$JETFAKES \
    --embedding=$EMBEDDING \
    --postfix="-ML" \
    --midfix="-${TAG}-" \
    --channel=${CHANNELS} \
    --auto_rebin=true \
    --stxs_signals=${STXS_SIGNALS} \
    --categories=${CATEGORIES} \
    --era=${ERA} \
    --output=${OUTPUTDIR} \
    --train_ff=${TRAIN_FF} \
    --train_stage0=${TRAIN_STAGE0} \
    --train_emb=${TRAIN_EMB} | tee output/log/datacard-${ERA}-${STXS_SIGNALS}-${CATEGORIES}-${JETFAKES}-${EMBEDDING}-${TAG}-${CHANNELS}.log

# Use Barlow-Beeston-lite approach for bin-by-bin systematics
for folder in "et" "mt" "tt" "em" "cmb"
    do
    for FILE in ${OUTPUTDIR}/${folder}/125/*.txt
    do
        sed -i '$s/$/\n * autoMCStats 0.0/' ${FILE}
    done
done
