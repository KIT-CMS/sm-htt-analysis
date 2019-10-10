#!/bin/bash
PWD=$1
cd $PWD

NUMCORES=$2
ERA=$3
VARIABLE=$4
CHANNEL=$5

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes
./cut_optimization/produce_soverb_cuts.sh $NUMCORES $ERA $VARIABLE $CHANNEL
