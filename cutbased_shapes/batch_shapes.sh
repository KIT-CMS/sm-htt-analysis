#!/bin/bash
PWD=$1
cd $PWD

NUMCORES=$2
ERA=$3
VARIABLE=$4
SHAPEGROUP=$5
CATEGORY=$6
CHANNEL=$7

# Produce shapes
./cutbased_shapes/produce_shapes.sh ${NUMCORES} ${ERA} ${VARIABLE} ${SHAPEGROUP} ${CATEGORY} ${CHANNEL}

echo "To normalize fake-factor shapes to nominal, execute the following, after the jobs are ready:"
echo
echo "hadd -f ${ERA}_cutbased_shapes_${VARIABLE}.root ${ERA}_??_*_cutbased_shapes_${VARIABLE}.root"
echo "python fake-factor-application/normalize_shifts.py ${ERA}_cutbased_shapes_${VARIABLE}.root"
