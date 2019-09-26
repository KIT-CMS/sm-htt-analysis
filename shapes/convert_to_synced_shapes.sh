#!/bin/bash
set -e
ERA=$1
CHANNELS=$2
TAG=$3


source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
python shapes/convert_to_synced_shapes.py \
    --era ${ERA} \
    --tag ${TAG} \
    --input output/shapes/${ERA}-${TAG}-${CHANNELS}-shapes.root \
    --output output/shapes
