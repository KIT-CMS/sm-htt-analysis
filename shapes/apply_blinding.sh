#!/bin/bash

ERA=$1
CHANNEL=$2
TAG=$3

source utils/setup_cvmfs_sft.sh

python shapes/apply_blinding.py output/shapes/${TAG}/${ERA}-${TAG}-${CHANNEL}-shapes.root \
    --threshold 0.5 --uncertainty 0.09 \
    --signal-processes ggH qqH VH \
    --exclude-categories _ss _B _sumW _sumEWKZ _FF
