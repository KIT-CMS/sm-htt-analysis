#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
CHANNELS=${@:2}

mkdir -p plots
for FILE in "datacard_shapes_prefit.root" "datacard_shapes_postfit_sb.root"
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes.py -i $FILE -c $CHANNELS -e $ERA $OPTION
    done
done
