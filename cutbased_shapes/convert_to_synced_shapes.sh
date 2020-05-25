#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
NUM_CORES=35

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

#python cutbased_shapes/convert_to_synced_shapes.py ${NUM_CORES} ${ERA} ${VARIABLE} output/shapes/${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root ${PWD}/output/shapes/
python cutbased_shapes/convert_to_synced_shapes.py ${NUM_CORES} ${ERA} ${VARIABLE} output/shapes/${ERA}_${CHANNEL}_${VARIABLE}/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}-${CHANNEL}-shapes.root ${PWD}/output/shapes/
