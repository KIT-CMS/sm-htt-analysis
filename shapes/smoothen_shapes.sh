#!/bin/bash

ERA=$1
CHANNELS=${@:2}

source utils/setup_cvmfs_sft.sh

python shapes/smoothen_shapes.py --era $ERA --channels $CHANNELS