#!/bin/bash

ERA=$1
CHANNEL=$2
TARGET_PROCESS=$3
VARIABLE1=$4
VARIABLE2=$5

WEIGHT_BRANCH=training_weight

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python ml/plot_training_variable_2d.py $ERA $CHANNEL $TARGET_PROCESS $VARIABLE1 $VARIABLE2 $WEIGHT_BRANCH
