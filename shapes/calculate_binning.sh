#!/bin/bash

ERA=$1
BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

# NOTE: Make the prefit shapes directly from the text datacards with the following command:
#       PostFitShapes -m 125 -d output/2016_smhtt/cmb/125/combined.txt.cmb -o 2016_datacard_shapes_prefit.root

python shapes/calculate_binning.py \
    --input ${ERA}_datacard_shapes_prefit.root \
    --era ${ERA}
