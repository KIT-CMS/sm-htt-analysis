#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

mkdir -p plots
./plotting/plot_shapes.py -i ${ERA}_datacard_shapes_prefit.root -e $ERA -c $CHANNEL --gof-variable $VARIABLE
./plotting/plot_shapes.py -i ${ERA}_datacard_shapes_prefit.root -e $ERA -c $CHANNEL --gof-variable $VARIABLE --png
./plotting/plot_shapes.py -i ${ERA}_datacard_shapes_postfit_sb.root -e $ERA -c $CHANNEL --gof-variable $VARIABLE
./plotting/plot_shapes.py -i ${ERA}_datacard_shapes_postfit_sb.root -e $ERA -c $CHANNEL --gof-variable $VARIABLE --png
