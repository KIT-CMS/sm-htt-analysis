#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python shapes/convert_to_synced_shapes.py ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root .
