#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
VARIABLE=$2
SHAPEDIR=$3

mkdir -p ${ERA}_plots_metrecoilfit
./recoil_corrections/plot_shapes.py -i $SHAPEDIR -e $ERA -v $VARIABLE
