#!/bin/bash

BINNING=shapes/binning.yaml
CHANNEL=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh

if [[ $1 =~ "et" ]]; then
    ARTUS_FRIENDS=$ARTUS_FRIENDS_ET
elif [[ $1 =~ "mt" ]]; then
    ARTUS_FRIENDS=$ARTUS_FRIENDS_MT
elif [[ $1 =~ "tt" ]]; then
    ARTUS_FRIENDS=$ARTUS_FRIENDS_TT
else
    echo "Channel $1 is not known. Exit."
    exit
fi

python shapes/calculate_binning.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --output $BINNING \
    --artus-friends $ARTUS_FRIENDS \
    --channel $1 \
    --training-config ml/${CHANNEL}_training_config.yaml
