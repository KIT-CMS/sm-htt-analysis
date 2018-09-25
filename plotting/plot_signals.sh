#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
STXS_SIGNALS=$2
CATEGORIES=$3
CHANNELS=${@:4}

mkdir -p plots
for FILE in "${ERA}_datacard_shapes_prefit.root" # "${ERA}_datacard_shapes_postfit_sb.root" # NOTE: Do this only prefit for now.
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_signals.py -i $FILE -c $CHANNELS -e $ERA $OPTION --categories $CATEGORIES --stxs-signals $STXS_SIGNALS
    done
done
