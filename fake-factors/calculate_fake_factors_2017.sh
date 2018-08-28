#!/bin/bash

ERA=$1
CONFIGKEY=$2

source utils/setup_cmssw_for_ff.sh
source utils/setup_python.sh
source utils/setup_samples_2017.sh

python fake-factors/calculate_fake_factors_2017.py --era $ERA \
        --directory $ARTUS_OUTPUTS \
        -c $CONFIGKEY \
        --et-fake-factor-directory CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data/SM2016_ML/180504_tight/et/fakeFactors_20180412_tight.root \
        --mt-fake-factor-directory CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data/SM2016_ML/180504_tight/mt/fakeFactors_20180406_tight.root \
        --tt-fake-factor-directory CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data/SM2016_ML/180504_tight/tt/fakeFactors_tt_inclusive.root \
        --num-threads 46
