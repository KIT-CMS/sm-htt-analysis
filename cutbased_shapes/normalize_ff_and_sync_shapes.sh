#!/bin/bash

source utils/setup_cvmfs_sft.sh

ERA=$1
CHANNEL=$2
VARIABLE=$3

# hadd -f ${ERA}_cutbased_shapes_${VARIABLE}.root ${ERA}_??_*_cutbased_shapes_${VARIABLE}.root
python fake-factor-application/normalize_shifts.py output/shapes/${ERA}_${CHANNEL}_${VARIABLE}_cutbased_shapes_${VARIABLE}.root

./cutbased_shapes/convert_to_synced_shapes.sh ${ERA} ${CHANNEL} ${VARIABLE}


