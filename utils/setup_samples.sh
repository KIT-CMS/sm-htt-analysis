#!/bin/bash

ERA=$1

basedir="/ceph/htautau"
# Samples Run2016
ARTUS_OUTPUTS_2016="$basedir/2016/ntuples"
NNScore_Friends_2016="$basedir/2016/nnscore_friends"
SVFit_Friends_2016="$basedir/2016/svfit_friends"
MELA_Friends_2016="$basedir/2016/mela_friends"
FF_Friends_2016="$basedir/2016/ff_friends"
ARTUS_FRIENDS_2016="$NNScore_Friends_2016 $SVFit_Friends_2016 $MELA_Friends_2016"
ARTUS_FRIENDS_ET_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_MT_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_TT_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_EM_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_FAKE_FACTOR_2016=$basedir/2016/ff_friends
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016=$ARTUS_FRIENDS_FAKE_FACTOR_2016


# Samples Run2017
ARTUS_OUTPUTS_2017="$basedir/2017/ntuples/"
NNScore_Friends_2017="$basedir/2017/nnscore_friends"
SVFit_Friends_2017="$basedir/2017/svfit_friends"
MELA_Friends_2017="$basedir/2017/mela_friends"
FF_Friends_2017="$basedir/2017/ff_friends"
ARTUS_FRIENDS_2017="$NNScore_Friends_2017 $SVFit_Friends_2017 $MELA_Friends_2017"
ARTUS_FRIENDS_ET_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_MT_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_TT_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_EM_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_FAKE_FACTOR_2017=$FF_Friends_2017
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=$FF_Friends_2017
ARTUS_OUTPUTS_EM_2017=blank

# Samples Run2018
# ARTUS_OUTPUTS_2018="$basedir/2018/ntuples"
# NNScore_Friends_2018="$basedir/2018/nnscore_friends"
# SVFit_Friends_2018="$basedir/2018/svfit_friends"
# MELA_Friends_2018="$basedir/2018/mela_friends"
# FF_Friends_2018="$basedir/2018/ff_friends"
# ARTUS_FRIENDS_2018="$NNScore_Friends_2018 $SVFit_Friends_2018 $MELA_Friends_2018"
# ARTUS_FRIENDS_ET_2018=$ARTUS_FRIENDS_2018
# ARTUS_FRIENDS_MT_2018=$ARTUS_FRIENDS_2018
# ARTUS_FRIENDS_TT_2018=$ARTUS_FRIENDS_2018
# ARTUS_FRIENDS_EM_2018=$ARTUS_FRIENDS_2018
# ARTUS_FRIENDS_FAKE_FACTOR_2018=$basedir/2018/ff_friends
# ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018=$ARTUS_FRIENDS_FAKE_FACTOR_2018
#############
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
    ARTUS_FRIENDS_ET=$ARTUS_FRIENDS_ET_2016
    ARTUS_FRIENDS_MT=$ARTUS_FRIENDS_MT_2016
    ARTUS_FRIENDS_TT=$ARTUS_FRIENDS_TT_2016
    ARTUS_FRIENDS_EM=$ARTUS_FRIENDS_EM_2016
    ARTUS_FRIENDS_FAKE_FACTOR=$ARTUS_FRIENDS_FAKE_FACTOR_2016
    ARTUS_FRIENDS_FAKE_FACTOR_INCL=$ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016
elif [[ $ERA == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    ARTUS_OUTPUTS_EM=$ARTUS_OUTPUTS_EM_2017
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
KAPPA_DATABASE=datasets/datasets.json
