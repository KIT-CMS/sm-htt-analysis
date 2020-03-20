#!/bin/bash
PWD=$1
cd $PWD

NUMCORES=$2
ERA=$3
VARIABLE=$4
PROCESS=$5
CATEGORY=$6
CHANNEL=$7

# Produce shapes
./cutbased_shapes/produce_shapes.sh ${NUMCORES} ${ERA} ${VARIABLE} ${PROCESS} ${CATEGORY} ${CHANNEL}
