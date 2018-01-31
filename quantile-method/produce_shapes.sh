#!/bin/bash

BINNING=shapes/binning.yaml
CHANNELS=$@

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

# Calculate binning from data distributions
# NOTE: Binning is now committed in repository.
#./shapes/calculate_binning.sh $ARTUS_OUTPUTS $KAPPA_DATABASE $ET_TRAINING $MT_TRAINING

# Produce shapes
python quantile-method/produce_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    -f /storage/c/swozniewski/SM_Htautau/ntuples/Artus_2018-01-17_ll/calibrated

