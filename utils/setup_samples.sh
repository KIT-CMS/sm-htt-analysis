#!/bin/bash

ERA=$1

# Samples Run2016
ARTUS_OUTPUTS_2016=/storage/c/swozniewski/SM_Htautau/ntuples/Artus_2018-08-21/merged
ARTUS_FRIENDS_ET_2016=/storage/c/swozniewski/SM_Htautau/ntuples/Artus_2018-08-21/et_keras_1
ARTUS_FRIENDS_MT_2016=/storage/c/swozniewski/SM_Htautau/ntuples/Artus_2018-08-21/mt_keras_1
ARTUS_FRIENDS_TT_2016=/storage/c/swozniewski/SM_Htautau/ntuples/Artus_2018-08-21/tt_keras_1
ARTUS_FRIENDS_FAKE_FACTOR_2016=/storage/c/swozniewski/SM_Htautau/ntuples/Artus_2018-08-21/fake_factor_friends_NN_score

# Samples Run2017
ARTUS_OUTPUTS_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_2018-10-01/merged
ARTUS_FRIENDS_ET_2017=/ceph/wunsch/Artus17_2018-10-01/et_keras_1
ARTUS_FRIENDS_MT_2017=/ceph/wunsch/Artus17_2018-10-01/mt_keras_1
ARTUS_FRIENDS_TT_2017=/ceph/wunsch/Artus17_2018-10-01/tt_keras_1
ARTUS_FRIENDS_FAKE_FACTOR_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_2018-10-01/fake_factor_friends_NN_score

# Error-handling
if [[ $ERA == *"2016"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2016
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2016
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2016
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2016
elif [[ $ERA == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2017
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2017
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2017
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2017
else
    echo "[ERROR] Era $ERA is not implemented." 1>&2
    read -p "Press any key to continue... " -n1 -s
fi

# Kappa database
KAPPA_DATABASE=/storage/c/wunsch/kappa_database/datasets_2018-08-01.json
