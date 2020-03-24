#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
JETFAKES=$4
EMBEDDING=$5

STXS_SIGNALS="stxs_stage0"
CATEGORIES="None"

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

EMBEDDING_ARG=""
OUTPUT_DIR=output/plots/${ERA}-control-plots/${CHANNEL}/classic-ff
if [ $EMBEDDING == 1 ]
then
    EMBEDDING_ARG="--embedding"
    OUTPUT_DIR=output/plots/${ERA}-control-plots/${CHANNEL}/emb-ff
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

if [[ ! -d $OUTPUT_DIR ]]
then
    mkdir -p $OUTPUT_DIR
fi
for FILE in "output/shapes/${ERA}-${CHANNEL}-${VARIABLE}-control-datacard-shapes-prefit.root" # "${ERA}_datacard_shapes_postfit_sb.root"
do
    for OPTION in "" "--png"
    do
        logandrun ./plotting/plot_shapes_gof.py -i $FILE -c $CHANNEL -e $ERA $OPTION \
            --categories $CATEGORIES $JETFAKES_ARG $EMBEDDING_ARG \
            --gof-variable $VARIABLE -o $OUTPUT_DIR --linear
    done
done
