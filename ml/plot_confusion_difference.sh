#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

DIFFERENCE=1
if [ -n "$DIFFERENCE" ]; then
python ml/plot_confusion_difference.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL} ml/${ERA}_${CHANNEL}_MELA 0
python ml/plot_confusion_difference.py \
    ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL} ml/${ERA}_${CHANNEL}_MELA 1
fi