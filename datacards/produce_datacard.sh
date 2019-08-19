#!/bin/bash
set -e
source utils/setup_cmssw.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

ERA=$1
STXS_SIGNALS=$2
CATEGORIES=$3
JETFAKES=$4
EMBEDDING=$5
TRAINING_METHOD=$6
CHANNELS=$7
NUM_THREADS=8
    if [[ $TRAINING_METHOD  =~ "emb" ]]; then
        TRAIN_EMB=1
    else
        TRAIN_EMB=0
    fi
    if [[ $TRAINING_METHOD =~ "ff" ]]; then
        TRAIN_FF=1
    else
        TRAIN_FF=0
    fi
OUTPUTDIR="output/datacards/${ERA}-${TRAINING_METHOD}-smhtt-ML/${STXS_SIGNALS}"

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
    --midfix="-${TRAINING_METHOD}-" \
    --channel=${CHANNELS} \
    --auto_rebin=true \
    --stxs_signals=${STXS_SIGNALS} \
    --categories=${CATEGORIES} \
    --era=${ERA} \
    --output=${OUTPUTDIR} \
    --train_ff=${TRAIN_FF} \
    --train_emb=${TRAIN_EMB} | tee output/log/datacard-${ERA}-${STXS_SIGNALS}-${CATEGORIES}-${JETFAKES}-${EMBEDDING}-${TRAINING_METHOD}-${CHANNELS}.log
        #--output="${ERA}_${TRAINING_METHOD}_smhtt" \

# Use Barlow-Beeston-lite approach for bin-by-bin systematics
THIS_PWD=${PWD}
echo $THIS_PWD
cd ${OUTPUTDIR}/cmb/125/
for FILE in *.txt
do
    sed -i '$s/$/\n * autoMCStats 0.0/' ${FILE}
done
cd ${THIS_PWD}
