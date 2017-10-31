#!/bin/bash

TRAINING=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python shapes/produce_shapes.py --training $TRAINING
