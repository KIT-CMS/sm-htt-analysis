#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

CHANNELS=$1
VARIABLE=$2
mkdir -p plots
for FILE in "datacard_shapes_prefit.root"
do
    for OPTION in "" "--png"
    do
		
    ./plotting/plot_shapes.py -i $FILE -c $CHANNELS \
    --gof-variable $VARIABLE $OPTION \
    -l 
    done
done
