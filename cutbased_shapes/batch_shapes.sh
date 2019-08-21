#!/bin/bash
PWD=$1
cd $PWD

NUMCORES=$2
ERA=$3
VARIABLE=$4
SHAPEGROUP=$5
CHANNEL=$6

source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
./cutbased_shapes/produce_shapes.sh ${NUMCORES} ${ERA} ${VARIABLE} ${SHAPEGROUP} ${CHANNEL}

echo "To normalize fake-factor shapes to nominal, execute the following, after the jobs are ready:"
echo
echo "hadd -f ${ERA}_${CHANNEL}_cutbased_shapes_${VARIABLE}.root ${ERA}_${CHANNEL}_${SHAPEGROUP}_cutbased_shapes_${VARIABLE}.root"
echo "python fake-factor-application/normalize_shifts.py ${ERA}_${CHANNEL}_cutbased_shapes_${VARIABLE}.root"
