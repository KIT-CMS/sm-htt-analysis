#!/bin/bash

ERA=$1

# Samples Run2016
ARTUS_OUTPUTS_2016=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/merged_fixedjets2
ARTUS_FRIENDS_ET_2016=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/et_keras_20190124
ARTUS_FRIENDS_MT_2016=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/mt_keras_20190124
ARTUS_FRIENDS_TT_2016=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/tt_keras_20190124
ARTUS_FRIENDS_FAKE_FACTOR_2016=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus16_Nov/Artus_2016_Jan19/fake_factor_friends_njets_mvis_NEW_NN_Jan27
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016=$ARTUS_FRIENDS_FAKE_FACTOR_2016
ARTUS_OUTPUTS_EM_2016=/invalidceph/jbechtel/2016/em_all_vars_JetFix_def


# Samples Run2017
#ARTUS_OUTPUTS_2017=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus17_Jan/merged_fixedjets
ARTUS_OUTPUTS_2017=/portal/ekpbms1/home/mburkart/workdir/Postprocessing_MSSM/mssm-htt-analysis/inputs/merged/
ARTUS_FRIENDS_ET_2017=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus17_Jan/et_keras_20190125
ARTUS_FRIENDS_MT_2017=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus17_Jan/mt_keras_20190125
ARTUS_FRIENDS_TT_2017=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus17_Jan/tt_keras_20190125
ARTUS_FRIENDS_FAKE_FACTOR_2017=/invalidceph/swozniewski/SM_Htautau/ntuples/Artus17_Jan/fake_factor_friends_njets_mvis_NEW_NN_Jan26
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=$ARTUS_FRIENDS_FAKE_FACTOR_2017
ARTUS_OUTPUTS_EM_2017=/portal/ekpbms1/home/jbechtel/postprocessing/em_all_vars_new/files

# Samples Run2018
ARTUS_OUTPUTS_2018=/portal/ekpbms1/home/jbechtel/postprocessing/2018/sm-htt-analysis/files
ARTUS_FRIENDS_ET_2018=blank
ARTUS_FRIENDS_MT_2018=blank
ARTUS_FRIENDS_TT_2018=blank
ARTUS_FRIENDS_FAKE_FACTOR_2018=blank
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018=blank
ARTUS_OUTPUTS_EM_2018=$ARTUS_OUTPUTS_2018

# Error-handling
if [[ $ERA == *"2016"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    ARTUS_OUTPUTS_EM=$ARTUS_OUTPUTS_EM_2016
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2016
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2016
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2016
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2016
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016
elif [[ $ERA == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    ARTUS_OUTPUTS_EM=$ARTUS_OUTPUTS_EM_2017
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2017
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2017
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2017
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2017
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017
elif [[ $ERA == *"2018"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2018
    ARTUS_OUTPUTS_EM=$ARTUS_OUTPUTS_EM_2018
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2018
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2018
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2018
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2018
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018
fi

# Kappa database
KAPPA_DATABASE=/portal/ekpbms1/home/jbechtel/postprocessing/2018/sm-htt-analysis/datasets.json
