#!/bin/bash

ERA=$1

source utils/setup_cvmfs_sft.sh

python shapes/apply_blinding.py ${ERA}_shapes.root --threshold 0.5 --uncertainty 0.09
