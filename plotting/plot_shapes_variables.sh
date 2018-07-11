#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
CHANNELS=$2
VARIABLE=$3
mkdir -p plots
for FILE in "${ERA}_shapes.root"
do
    for OPTION in "" "--png"
    do
		
    ./plotting/plot_shapes.py -i $FILE -c $CHANNELS --era $ERA --stxs-categories 0 \
    --gof-variable $VARIABLE $OPTION \
    -l 
    done
done
