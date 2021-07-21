#!/bin/bash

ERA=$1
CHANNEL=$2
ANALYSIS_NAME=$3
MASS=$4
BATCH=$5




./ml/translate_models.sh $ERA $CHANNEL $ANALYSIS_NAME 
./ml/export_lwtnn.sh $ERA $CHANNEL $ANALYSIS_NAME $MASS $BATCH
