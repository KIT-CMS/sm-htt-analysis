#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
CATEGORIES=$3
JETFAKES=$4
EMBEDDING=$5
CHANNELS=${@:6}

if [ $STXS_SIGNALS == 1 ]
then
    echo "[ERROR] Plotting for STXS stage 1 signals is not yet implemented."
    exit
fi

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

mkdir -p ${ERA}_plots
for FILE in "${ERA}_datacard_shapes_prefit.root" "${ERA}_datacard_shapes_postfit_sb.root"
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes.py -i $FILE -c $CHANNELS -e $ERA $OPTION --categories $CATEGORIES $JETFAKES_ARG $EMBEDDING_ARG --normalize-by-bin-width -l
    done
done
