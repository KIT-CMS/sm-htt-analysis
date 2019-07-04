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
ARTUS_OUTPUTS_2017=/storage/b/akhmet/merged_files_from_naf/Full_2017_test_all-channels
#ARTUS_FRIENDS_ET_2017="/storage/b/akhmet/merged_files_from_naf/MELA_collected /storage/b/akhmet/merged_files_from_naf/SVFit_collected /storage/b/akhmet/merged_files_from_naf/NNScore_collected"
#ARTUS_FRIENDS_MT_2017="/storage/b/akhmet/merged_files_from_naf/MELA_collected /storage/b/akhmet/merged_files_from_naf/SVFit_collected /storage/b/akhmet/merged_files_from_naf/NNScore_collected"
#ARTUS_FRIENDS_TT_2017="/storage/b/akhmet/merged_files_from_naf/MELA_collected /storage/b/akhmet/merged_files_from_naf/SVFit_collected /storage/b/akhmet/merged_files_from_naf/NNScore_collected"
#ARTUS_FRIENDS_EM_2017="/storage/b/akhmet/merged_files_from_naf/MELA_collected /storage/b/akhmet/merged_files_from_naf/SVFit_collected /storage/b/akhmet/merged_files_from_naf/NNScore_collected"
#ARTUS_FRIENDS_ET_2017=/storage/b/sjoerger/pruning/et/complete_analysis/6_variables/
#ARTUS_FRIENDS_EM_2017=/storage/b/sjoerger/pruning/em/complete_analysis/18_variables/
#ARTUS_FRIENDS_TT_2017=/storage/b/sjoerger/pruning/tt/complete_analysis/7_variables/
#ARTUS_FRIENDS_MT_2017=/storage/b/sjoerger/pruning/mt/complete_analysis/7_variables/
#ARTUS_FRIENDS_ET_2017=/storage/b/sjoerger/MELA/all_channels
#ARTUS_FRIENDS_EM_2017=/storage/b/sjoerger/MELA/all_channels
#ARTUS_FRIENDS_TT_2017=/storage/b/sjoerger/MELA/all_channels
#ARTUS_FRIENDS_MT_2017=/storage/b/sjoerger/MELA/all_channels
#ARTUS_FRIENDS_ET_2017=/storage/b/sjoerger/pruning/combined/pruned
#ARTUS_FRIENDS_EM_2017=/storage/b/sjoerger/pruning/combined/pruned
#ARTUS_FRIENDS_TT_2017=/storage/b/sjoerger/pruning/combined/pruned
#ARTUS_FRIENDS_MT_2017=/storage/b/sjoerger/pruning/combined/pruned
ARTUS_FRIENDS_ET_2017=/storage/b/sjoerger/pruning/combined/11variables
ARTUS_FRIENDS_EM_2017=/storage/b/sjoerger/pruning/combined/11variables
ARTUS_FRIENDS_TT_2017=/storage/b/sjoerger/pruning/combined/11variables
ARTUS_FRIENDS_MT_2017=/storage/b/sjoerger/pruning/combined/11variables
ARTUS_FRIENDS_FAKE_FACTOR_2017=/home/mscham/data/fake_factor_friends_2017_m_vis_inclusive/
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=$ARTUS_FRIENDS_FAKE_FACTOR_2017

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
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2017
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2017
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2017
    ARTUS_FRIENDS_EM=$ARTUS_FRIENDS_EM_2017
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2017
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017
elif [[ $ERA == *"2018"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2018
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2018
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2018
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2018
    ARTUS_FRIENDS_EM=$ARTUS_FRIENDS_EM_2018
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2018
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018
fi

# Kappa database
KAPPA_DATABASE=/storage/b/akhmet/kappa_databases/datasets.json
