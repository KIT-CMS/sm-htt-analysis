#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

CHANNELS=$1
VARIABLE=$2
LABELING=Dumbledraw/Dumbledraw/labels.yaml
mkdir -p plots
for FILE in "datacard_shapes_prefit.root" "datacard_shapes_postfit_sb.root"
do
    for OPTION in "" "--png"
    do
		if [ -z $VARIABLE ]; then
		./plotting/plot_shapes.py -i $FILE -c $CHANNELS $OPTION
		else
		./plotting/plot_shapes.py -i $FILE -c $CHANNELS \
		--gof-variable $VARIABLE $OPTION \
		--x_label $LABELING
		fi
    done
done
