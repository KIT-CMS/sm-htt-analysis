#!/bin/bash

ERA=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

source utils/bashFunctionCollection.sh

logandrun python gof/create_jdl.py $ERA $OUTPUT gof/${ERA}_binning.yaml gof/variables.yaml

# Change line in 
