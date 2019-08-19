#!/bin/bash
set -e
ERA=$1
CHANNELS=$2
METHOD=$3


source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
python shapes/convert_to_synced_shapes.py \
    --era ${ERA} \
    --train-method ${METHOD} \
    --input output/shapes/${ERA}-${METHOD}-${CHANNELS}-shapes.root \
    --output output/shapes