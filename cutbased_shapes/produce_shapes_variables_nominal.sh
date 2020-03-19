#!/bin/bash

BINNING=cutbased_shapes/binning.yaml
ERA=$1
CHANNELS=$2
VARIABLE=$3
CATEGORY=$4
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions
# NOTE: Binning is committed in this repository.
#./shapes/calculate_binning.sh et
#./shapes/calculate_binning.sh mt
#./shapes/calculate_binning.sh tt

# Produce shapes


python cutbased_shapes/produce_nmssm_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --em-friend-directory "" \
    --et-friend-directory "" \
    --mt-friend-directory "" \
    --tt-friend-directory "" \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --discriminator-variable $VARIABLE \
    --era $ERA \
    --num-threads 2 \
    --tag ${ERA}_${CHANNELS}_${VARIABLE} \
	--skip-systematic-variations
