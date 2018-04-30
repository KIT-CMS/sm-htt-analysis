#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
BINNING=gof/${ERA}_binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions if file is not existent
if [ ! -f "$BINNING" ]
then
    python gof/calculate_binning.py \
        --era $ERA \
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
    --era $ERA \
    --num-threads 1

# Apply blinding strategy
./shapes/apply_blinding.sh $ERA
