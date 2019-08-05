#!/bin/bash

ERA=$1
VARIABLE=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python recoil_corrections/convert_to_synced_shapes.py ${ERA} ${VARIABLE} fitrecoil_mm_${ERA}.root .
