#!/bin/bash

BINNING=cutbased_shapes/binning.yaml
ERA=$1
CHANNEL=$2
VARIABLE=$3
N_THREADS=$4
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
    --em-friend-directory $SVFit_Friends \
    --et-friend-directory $SVFit_Friends $TauTriggers_Friends \
    --mt-friend-directory $SVFit_Friends $TauTriggers_Friends \
    --tt-friend-directory $SVFit_Friends $TauTriggers_Friends \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channel $CHANNEL \
    --discriminator-variable $VARIABLE \
    --era $ERA \
    --num-threads $N_THREADS \
    --tag ${ERA}_${CHANNEL}_${VARIABLE}
