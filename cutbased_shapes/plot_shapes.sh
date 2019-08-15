#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
FILE=$2
VARIABLE=$3

./cutbased_shapes/plot_shapes.py -i $FILE -e $ERA --normalize-by-bin-width  -v $VARIABLE -t prefit
