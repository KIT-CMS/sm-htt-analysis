#!/bin/bash

ERA=$1
OUTPUT=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

source utils/bashFunctionCollection.sh

python gof/create_jdl.py $ERA $OUTPUT gof/${ERA}_binning.yaml gof/variables.yaml
