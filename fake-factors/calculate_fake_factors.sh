#!/bin/bash

ERA=$1
CONFIGKEY=$2
CATEGORYMODE=$3

source utils/setup_cmssw_for_ff.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

if [[ $ERA == *"2016"* ]]
then
    FF_database_ET=CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data_2016/SM2016_ML/tight/et/fakeFactors_tight.root
    FF_database_MT=CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data_2016/SM2016_ML/tight/mt/fakeFactors_tight.root
    FF_database_TT=CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data_2016/SM2016_ML/tight/tt/fakeFactors_tight.root
    FF_workspce=fake-factors/htt_ff_fractions_2016.xroot
    USE_WORKSPACE="" #change to -w to use fracctions from workspace
elif [[ $ERA == *"2017"* ]]
then
    FF_database_ET=CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data_2017/SM2017/tight/vloose/et/fakeFactors.root
    FF_database_MT=CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data_2017/SM2017/tight/vloose/mt/fakeFactors.root
    FF_database_TT=CMSSW_8_0_4/src/HTTutilities/Jet2TauFakes/data_2017/SM2017/tight/vloose/tt/fakeFactors.root
    FF_workspce=""
    USE_WORKSPACE=""
fi

python fake-factors/calculate_fake_factors.py --era $ERA \
        --directory $ARTUS_OUTPUTS \
        --et-friend-directory $ARTUS_FRIENDS_ET \
        --mt-friend-directory $ARTUS_FRIENDS_MT \
        --tt-friend-directory $ARTUS_FRIENDS_TT \
        -c $CONFIGKEY \
        --et-fake-factor-directory $FF_database_ET \
        --mt-fake-factor-directory $FF_database_MT \
        --tt-fake-factor-directory $FF_database_TT \
        --num-threads 12 \
        --category-mode $CATEGORYMODE \
        --workspace $FF_workspce $USE_WORKSPACE
