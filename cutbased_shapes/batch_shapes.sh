#!/bin/bash
PWD=$1
cd $PWD

NUM_CORES=$2
ERA=$3
VARIABLE=$4
SHAPEGROUP=$5
CHANNEL=$6

source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python cutbased_shapes/produce_shapes.sh ${NUM_CORES} ${ERA} ${VARIABLE} ${SHAPEGROUP} ${CHANNEL}

echo "To normalize fake-factor shapes to nominal, execute the following, after the jobs are ready:"
echo
echo "hadd -f {ERA}_${CHANNELS}_cutbased_shapes_${VARIABLE}.root {ERA}_${CHANNELS}_${SHAPEGROUP}_cutbased_shapes_${VARIABLE}.root"
echo "python fake-factor-application/normalize_shifts.py ${ERA}_${CHANNELS}_cutbased_shapes_${VARIABLE}.root"
