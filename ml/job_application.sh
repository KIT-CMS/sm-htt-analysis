#!/bin/bash

DATASET_CONFIG=$1
TRAINING_CONFIG=$2
ANALYSIS_CONFIG=$3
FILE=$4
FOLDERS=${@:5}

for FOLDER in $FOLDERS
do
python htt-ml/application/TMVA_application.py \
    $DATASET_CONFIG \
    $TRAINING_CONFIG \
    $ANALYSIS_CONFIG \
    $FILE \
    $FOLDER/ntuple
done
