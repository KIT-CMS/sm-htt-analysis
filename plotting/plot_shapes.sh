#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
STXS_CATEGORIES=$3
CHANNELS=${@:4}

if [ $STXS_SIGNALS == 1 ]
then
    echo "[ERROR] Plotting for STXS stage 1 signals is not yet implemented."
    exit
fi

mkdir -p plots
for FILE in "${ERA}_datacard_shapes_prefit.root" "${ERA}_datacard_shapes_postfit_sb.root"
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes.py -i $FILE -c $CHANNELS -e $ERA $OPTION --stxs-categories $STXS_CATEGORIES
    done
done
