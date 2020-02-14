#!/bin/bash
set -e
ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/bashFunctionCollection.sh

inputfile=${ERA}_shapes.root
[[ -f $inputfile ]] || ( logerror $inputfile not fould && exit 2 )
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
logandrun python shapes/convert_to_synced_shapes.py \
    --era ${ERA} \
    --tag ${VARIABLE} \
    --input $inputfile \
    --output output/control_shapes
