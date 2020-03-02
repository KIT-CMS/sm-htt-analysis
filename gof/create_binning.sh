#!/bin/bash

ERA=$1
BINNING=gof/${ERA}_binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions if file is not existent
for CHANNEL in em mt et tt
do
    python gof/calculate_binning.py \
        --era $ERA \
        --directory $ARTUS_OUTPUTS \
        --em-friend-directories $ARTUS_FRIENDS_EM \
        --et-friend-directories $ARTUS_FRIENDS_ET \
        --mt-friend-directories $ARTUS_FRIENDS_MT \
        --tt-friend-directories $ARTUS_FRIENDS_TT \
        --datasets $KAPPA_DATABASE \
        --output $BINNING \
        --variables gof/variables.yaml \
        --channel $CHANNEL
    mv gof/${ERA}_binning.yaml gof/${ERA}_${CHANNEL}_binning.yaml
done
