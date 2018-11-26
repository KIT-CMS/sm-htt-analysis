#!/bin/bash

ERA=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python shapes/convert_to_synced_shapes.py ${ERA} ${ERA}_shapes.root .
