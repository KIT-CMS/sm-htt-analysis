#!/bin/bash

CHANNEL=$1
VARIABLE=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

mkdir -p plots
./plotting/plot_shapes.py -i datacard_shapes_prefit.root -c $CHANNEL --x-label $VARIABLE --gof-variable $VARIABLE
./plotting/plot_shapes.py -i datacard_shapes_prefit.root -c $CHANNEL --x-label $VARIABLE --gof-variable $VARIABLE --png
./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -c $CHANNEL --x-label $VARIABLE --gof-variable $VARIABLE
./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -c $CHANNEL --x-label $VARIABLE --gof-variable $VARIABLE --png
