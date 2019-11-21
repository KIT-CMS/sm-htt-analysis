#!/bin/bash
set -e
ERA=$1
CHANNELS=$2
TAG=$3

source utils/bashFunctionCollection.sh

inputfile=output/shapes/${ERA}-${TAG}-${CHANNELS}-shapes.root
[[ -f $inputfile ]] || ( logerror $inputfile not fould && exit 2 )
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
logandrun python shapes/convert_to_synced_shapes.py \
    --era ${ERA} \
    --tag ${TAG} \
    --input $inputfile \
    --output output/shapes
