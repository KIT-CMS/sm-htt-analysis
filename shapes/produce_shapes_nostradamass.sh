#!/bin/bash

BINNING=shapes/binning.yaml
REST=$@
echo $REST

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

# Calculate binning from data distributions
# NOTE: Binning is committed in this repository.
#./shapes/calculate_binning.sh et
#./shapes/calculate_binning.sh mt
#./shapes/calculate_binning.sh tt

# Produce shapes
python shapes/produce_shapes_nostradamass.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
	$REST
#    --tt-friend-directory $ARTUS_FRIENDS_TT \
#    --mt-friend-directory $ARTUS_FRIENDS_MT \
#    --et-friend-directory $ARTUS_FRIENDS_ET \

	
