#!/bin/bash

BINNING=shapes/binning.yaml
CHANNELS=$1
VARIABLE=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

# Calculate binning from data distributions
# NOTE: Binning is committed in this repository.
#./shapes/calculate_binning.sh et
#./shapes/calculate_binning.sh mt
#./shapes/calculate_binning.sh tt

# Produce shapes

if [ -z $VARIABLE  ]; then
	python shapes/produce_shapes.py \
		--directory $ARTUS_OUTPUTS \
		--datasets $KAPPA_DATABASE \
		--et-friend-directory $ARTUS_FRIENDS_ET \
		--mt-friend-directory $ARTUS_FRIENDS_MT \
		--tt-friend-directory $ARTUS_FRIENDS_TT \
		--binning $BINNING \
		--emb \
		--channels $CHANNELS 
else
	python shapes/produce_shapes.py \
		--directory $ARTUS_OUTPUTS \
		--datasets $KAPPA_DATABASE \
		--binning $BINNING \
		--gof-channel $CHANNELS \
		--emb \
		--gof-variable $VARIABLE
fi
