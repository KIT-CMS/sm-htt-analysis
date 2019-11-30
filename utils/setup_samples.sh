#!/bin/bash
set -e

ERA=$1
TAG=$2
[[ ! -z $3 ]] && WD=$3 || WD=$( pwd -P )
# Samples Run2016
basedir="/ceph/htautau"
ARTUS_OUTPUTS_2016="$basedir/2016/ntuples/"
NNScore_Friends_2016=""
SVFit_Friends_2016="$basedir/2016/svfit_friends_v2/"
MELA_Friends_2016="$basedir/2016/mela_friends/"
FF_Friends_2016="$basedir/2016/ff_friends/"
if [[ -d output/friend_trees ]]; then
    DIR=${WD}/output/friend_trees/2016/nnscore_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && NNScore_Friends_2016=$DIR
    DIR=${WD}/output/friend_trees/2016/svfit_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && SVFit_Friends_2016=$DIR
    DIR=${WD}/output/friend_trees/2016/mela_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && MELA_Friends_2016=$DIR
    DIR=${WD}/output/friend_trees/2016/ff_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && FF_Friends_2016=$DIR
fi
ARTUS_FRIENDS_2016="$NNScore_Friends_2016 $MELA_Friends_2016 $SVFit_Friends_2016" # TODO update once friends are produced
ARTUS_FRIENDS_ET_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_MT_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_TT_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_EM_2016=$ARTUS_FRIENDS_2016

ARTUS_FRIENDS_FAKE_FACTOR_2016=$FF_Friends_2016
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016=$ARTUS_FRIENDS_FAKE_FACTOR_2016


# Samples Run2017
basedir="/ceph/htautau/deeptau"
ARTUS_OUTPUTS_2017="$basedir/2017/ntuples/"
NNScore_Friends_2017="$basedir/2017/friends/NNScore/"
SVFit_Friends_2017="$basedir/2017/friends/SVFit/"
MELA_Friends_2017="$basedir/2017/friends/MELA/"
FF_Friends_2017="$basedir/2017/friends/FakeFactors/"
if [[ -d output/friend_trees ]]; then
    DIR=${WD}/output/friend_trees/2017/friends/NNScore/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && NNScore_Friends_2017=$DIR
    DIR=${WD}/output/friend_trees/2017/friends/SVFit/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && SVFit_Friends_2017=$DIR
    DIR=${WD}/output/friend_trees/2017/friends/MELA/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && MELA_Friends_2017=$DIR
    DIR=${WD}/output/friend_trees/2017/friends/FakeFactors/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && FF_Friends_2017=$DIR
fi

ARTUS_FRIENDS_2017="$SVFit_Friends_2017 $MELA_Friends_2017 $NNScore_Friends_2017"
ARTUS_FRIENDS_ET_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_MT_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_TT_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_EM_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_FAKE_FACTOR_2017=$FF_Friends_2017
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=$FF_Friends_2017
ARTUS_OUTPUTS_EM_2017=""

# Samples Run2018
basedir="/ceph/htautau/deeptau"
ARTUS_OUTPUTS_2018="$basedir/2018/ntuples/"
NNScore_Friends_2018="$basedir/2018/friends/NNScore/"
SVFit_Friends_2018="$basedir/2018/friends/SVFit/"
MELA_Friends_2018="$basedir/2018/friends/MELA/"
FF_Friends_2018="$basedir/2018/friends/FakeFactors/"
if [[ -d output/friend_trees ]]; then
    DIR=${WD}/output/friend_trees/2018/friends/NNScore/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && NNScore_Friends_2017=$DIR
    DIR=${WD}/output/friend_trees/2018/friends/SVFit/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && SVFit_Friends_2017=$DIR
    DIR=${WD}/output/friend_trees/2018/friends/MELA/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && MELA_Friends_2017=$DIR
    DIR=${WD}/output/friend_trees/2018/friends/FakeFactors/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && FF_Friends_2017=$DIR
fi
ARTUS_FRIENDS_2018="$SVFit_Friends_2018 $MELA_Friends_2018 $NNScore_Friends_2018"
ARTUS_FRIENDS_ET_2018=$ARTUS_FRIENDS_2018
ARTUS_FRIENDS_MT_2018=$ARTUS_FRIENDS_2018
ARTUS_FRIENDS_TT_2018=$ARTUS_FRIENDS_2018
ARTUS_FRIENDS_EM_2018=$ARTUS_FRIENDS_2018
ARTUS_FRIENDS_FAKE_FACTOR_2018=$FF_Friends_2018
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018=$FF_Friends_2018



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
