#!/bin/bash

ERA=$1

# Samples Run2016
ARTUS_OUTPUTS_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/merged_fixedjets2
ARTUS_FRIENDS_ET_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/et_keras_20190124
ARTUS_FRIENDS_MT_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/mt_keras_20190124
ARTUS_FRIENDS_TT_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/tt_keras_20190124
ARTUS_FRIENDS_FAKE_FACTOR_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/fake_factor_friends_njets_mvis_NEW_NN_Jan27
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016/fake_factor_friends_njets_mvis_NEW_incl_Dec15

# Samples Run2017
ARTUS_OUTPUTS_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_Jan/merged_fixedjets
ARTUS_FRIENDS_ET_2017=/ceph/wunsch/Artus17_Jan/et_keras_20190125
ARTUS_FRIENDS_MT_2017=/ceph/wunsch/Artus17_Jan/mt_keras_20190125
ARTUS_FRIENDS_TT_2017=/ceph/wunsch/Artus17_Jan/tt_keras_20190125
ARTUS_FRIENDS_FAKE_FACTOR_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_Jan/fake_factor_friends_njets_mvis_NEW_NN_Jan26
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_NovPU/fake_factor_friends_njets_mvis_NEW_incl_Dec11

# Error-handling
if [[ $ERA == *"2016"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2016
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2016
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2016
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2016
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016
elif [[ $ERA == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2017
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2017
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2017
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2017
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017
else
    echo "[ERROR] Era $ERA is not implemented." 1>&2
    read -p "Press any key to continue... " -n1 -s
fi

# Kappa database
KAPPA_DATABASE=/ceph/swozniewski/kappa_database/datasets_2019_01_20.json
