#!/bin/bash

CHANNEL=$1
VARIABLE=$2

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils gof
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

# Clean-up workspace
./utils/clean.sh

# Setup
ARTUS_OUTPUTS=/storage/jbod/wunsch/Run2Analysis_alex_classified2
KAPPA_DATABASE=/portal/ekpbms1/home/wunsch/CMSSW_7_4_7/src/Kappa/Skimming/data/datasets.json
BINNING=gof/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

# Calculate binning from data distributions if file is not existent
if [ ! -f "$BINNING" ]
then
    python gof/calculate_binning.py \
        --directory $ARTUS_OUTPUTS \
        --datasets $KAPPA_DATABASE \
        --output $BINNING \
        --variables gof/variables.yaml
fi

# Produce shapes
python shapes/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --gof-channel $CHANNEL \
    --gof-variable $VARIABLE

# Apply blinding strategy
./shapes/apply_blinding.sh
