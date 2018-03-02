#!/bin/bash

CHANNEL=$1
VARIABLE=$2
BINNING=gof/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils gof
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

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
    --gof-variable $VARIABLE \
    --num-threads 1 \
    --emb

# Apply blinding strategy
./shapes/apply_blinding.sh
