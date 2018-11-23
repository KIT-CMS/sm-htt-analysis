#!/bin/bash

ERA=$1

# Samples Run2016
ARTUS_OUTPUTS_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016/merged
ARTUS_FRIENDS_ET_2016=/ceph/wunsch/Artus16_Nov/et_keras_13
ARTUS_FRIENDS_MT_2016=/ceph/wunsch/Artus16_Nov/mt_keras_13
ARTUS_FRIENDS_TT_2016=/ceph/wunsch/Artus16_Nov/tt_keras_13
ARTUS_FRIENDS_FAKE_FACTOR_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016/fake_factor_friends_njets_mvis
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016=/ceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016/fake_factor_friends_njets_mvis_incl

# Samples Run2017
ARTUS_OUTPUTS_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_Nov/merged
ARTUS_FRIENDS_ET_2017=/ceph/wunsch/Artus17_2018-10-01/et_keras_5
ARTUS_FRIENDS_MT_2017=/ceph/wunsch/Artus17_2018-10-01/mt_keras_5
ARTUS_FRIENDS_TT_2017=/ceph/wunsch/Artus17_2018-10-01/tt_keras_5
ARTUS_FRIENDS_FAKE_FACTOR_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_Nov/fake_factor_friends_njets_mvis_incl
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=/ceph/swozniewski/SM_Htautau/ntuples/Artus17_Nov/fake_factor_friends_njets_mvis_incl

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
KAPPA_DATABASE=/ceph/akhmet/kappa_database/datasets_2018_11_20.json
