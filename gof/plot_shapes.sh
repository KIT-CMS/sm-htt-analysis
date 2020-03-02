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
if [ $EMBEDDING == 1 ]
then
    EMBEDDING_ARG="--embedding"
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

if [[ ! -d output/gof/${ERA}-${CHANNEL}-${VARIABLE}/${ERA}_plots ]]
then
    mkdir -p output/gof/${ERA}-${CHANNEL}-${VARIABLE}/${ERA}_plots
fi
for FILE in "${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-prefit.root" "${ERA}-${CHANNEL}-${VARIABLE}-datacard-shapes-postfit-b.root"
do
    for OPTION in "" "--png"
    do
        logandrun ./plotting/plot_shapes_gof.py -i $FILE -c $CHANNEL -e $ERA $OPTION \
            --categories $CATEGORIES $JETFAKES_ARG $EMBEDDING_ARG \
            --gof-variable $VARIABLE -o output/gof/${ERA}-${CHANNEL}-${VARIABLE}/${ERA}_plots
    done
done
