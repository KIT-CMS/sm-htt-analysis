#!/bin/bash

BINNING=shapes/nmssm_binning.yaml
ERA=$1
CHANNELS=$2
VARIABLE=$3

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions
# NOTE: Binning is committed in this repository.
#./shapes/calculate_binning.sh et
#./shapes/calculate_binning.sh mt
#./shapes/calculate_binning.sh tt

# Produce shapes


python shapes/produce_nmssm_shapes_allProcesses.py \
    --directory $ARTUS_OUTPUTS \
    --em-friend-directory $HHKinFit_Friends $SVFit_Friends \
    --et-friend-directory $HHKinFit_Friends $SVFit_Friends \
    --mt-friend-directory $HHKinFit_Friends $SVFit_Friends \
    --tt-friend-directory $HHKinFit_Friends $SVFit_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --gof-variable $VARIABLE \
    --era $ERA \
    --num-threads 32 \
    --tag ${ERA}_${CHANNELS}_${VARIABLE} \
	--skip-systematic-variations true
