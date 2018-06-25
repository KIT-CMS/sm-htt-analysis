#!/bin/bash

ERA=$1
OUTPUTDIRECTORY=$2

source utils/setup_cmssw.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

python fake-factors/calculate_fake_factors.py --era $ERA \
        --directory $ARTUS_OUTPUTS \
        --et-friend-directory $ARTUS_FRIENDS_ET \
        --mt-friend-directory $ARTUS_FRIENDS_MT \
        --tt-friend-directory $ARTUS_FRIENDS_TT \
        -o $OUTPUTDIRECTORY \
        -f CMSSW_7_4_7/src/HTTutilities/Jet2TauFakes/data/SM2016_ML/180504_tight \
        --num-threads 2