#!/bin/bash

ERA=$1

# Samples Run2016
ARTUS_OUTPUTS_2016=/storage/c/wunsch/Artus_2018-07-26/merged
ARTUS_FRIENDS_ET_2016=/storage/c/wunsch/Artus_2018-07-26/et_keras_1
ARTUS_FRIENDS_MT_2016=/storage/c/wunsch/Artus_2018-07-26/mt_keras_1
ARTUS_FRIENDS_TT_2016=/storage/c/wunsch/Artus_2018-07-26/tt_keras_1
ARTUS_FRIENDS_FAKE_FACTOR=/storage/c/wunsch/Artus_2018-07-26/fake_factor_friends_NN_score

# Error-handling
if [[ $ERA == *"2016"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2016
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2016
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2016
else
    echo "[ERROR] Era $ERA is not implemented." 1>&2
    read -p "Press any key to continue... " -n1 -s
fi

# Kappa database
KAPPA_DATABASE=/storage/c/wunsch/kappa_database/datasets_2018-08-01.json
