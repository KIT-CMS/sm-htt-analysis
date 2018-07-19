#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
STXS_CATEGORIES=$3
JETFAKES=$4
EMBEDDING=$5
CHANNELS=${@:6}

if [ $STXS_SIGNALS == 1 ]
then
    echo "[ERROR] Plotting for STXS stage 1 signals is not yet implemented."
    exit
fi

if [ $EMBEDDING == 1 ]
then
    echo "[ERROR] Plotting for embedding ist not yet implemented."
    exit
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

mkdir -p plots
for FILE in "${ERA}_datacard_shapes_prefit.root" "${ERA}_datacard_shapes_postfit_sb.root"
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes.py -i $FILE -c $CHANNELS -e $ERA $OPTION --stxs-categories $STXS_CATEGORIES $JETFAKES_ARG
    done
done
