#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
JETFAKES=$4
EMBEDDING=$5

STXS_SIGNALS="stxs_stage0"
CATEGORIES="gof"

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

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

mkdir -p plots
for FILE in "${ERA}_datacard_shapes_prefit.root" # "${ERA}_datacard_shapes_postfit_sb.root"
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes.py -i $FILE -c $CHANNEL -e $ERA $OPTION \
            --categories $CATEGORIES $JETFAKES_ARG $EMBEDDING_ARG \
            --gof-variable $VARIABLE
    done
done
