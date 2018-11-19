#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
CHANNEL=$2
PROCESSES=${@:3}

python ml/taylor2latex.py --era ${ERA} --channel ${CHANNEL} --processes ${PROCESSES} --rows 50
