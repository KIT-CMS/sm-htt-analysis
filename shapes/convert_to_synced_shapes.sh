#!/bin/bash
set -e
ERA=$1
CHANNELS=$2
TAG=$3

source utils/bashFunctionCollection.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_98python3/x86_64-centos7-gcc9-opt/setup.sh

inputfile=output/shapes/${TAG}/${ERA}-${TAG}-${CHANNELS}-shapes.root
output=output/shapes/${ERA}-${TAG}-${CHANNELS}
[[ -f $inputfile ]] || ( logerror $inputfile not fould && exit 2 )

source utils/setup_python.sh
logandrun python shapes/convert_to_synced_shapes.py \
    --era ${ERA} \
    --tag ${TAG} \
    --input $inputfile \
    --output ${output}

hadd -f output/shapes/${ERA}-${TAG}-${CHANNELS}-synced-ML.root ${output}/*.root
