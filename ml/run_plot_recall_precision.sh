#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

SUMMARY_PLOT=1
if [ -n "$SUMMARY_PLOT" ]; then
python ml/plot_recall_precision.py \
    ml/${ERA}_${CHANNEL}_training_pruning_0.yaml 0
python ml/plot_recall_precision.py \
    ml/${ERA}_${CHANNEL}_training_pruning_1.yaml 1
fi