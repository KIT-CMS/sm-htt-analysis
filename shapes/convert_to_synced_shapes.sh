#!/bin/bash

ERA=$1
METHOD=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
(
set -x
python shapes/convert_to_synced_shapes.py \
    --era ${ERA} \
    --outmidname $METHOD \
    --input ${ERA}_${m}_shapes.root \
    --output .
)