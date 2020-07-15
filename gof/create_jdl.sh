#!/bin/bash

ERA=$1
CHANNEL=$2
OUTPUT=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

source utils/bashFunctionCollection.sh

logandrun python gof/create_jdl.py $ERA $OUTPUT gof/${ERA}_${CHANNEL}_binning.yaml gof/variables.yaml
