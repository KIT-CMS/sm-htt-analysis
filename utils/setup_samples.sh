#!/bin/bash
set -e

ERA=$1
TAG=$2
[[ ! -z $3 ]] && WD=$3 || WD=$( pwd -P )

# Kappa database
KAPPA_DATABASE=datasets/datasets.json

#### ERA specific part. If a sample is not available comment it out here.
# Samples Run2016
basedir="/ceph/htautau/deeptau_eoy"
ARTUS_OUTPUTS_2016="$basedir/2016/ntuples/"
#NNScore_Friends_2016="$basedir/2016/friends/NNScore/"
SVFit_Friends_2016="$basedir/2016/friends/SVFit/"
MELA_Friends_2016="$basedir/2016/friends/MELA/"
FF_Friends_2016="$basedir/2016/friends/FakeFactors_updated/"
TauTriggers_Friends_2016="$basedir/2016/friends/TauTriggers/"

# Samples Run2017
ARTUS_OUTPUTS_2017="$basedir/2017/ntuples/"
#NNScore_Friends_2017="$basedir/2017/friends/NNScore/"
SVFit_Friends_2017="$basedir/2017/friends/SVFit/"
MELA_Friends_2017="$basedir/2017/friends/MELA/"
FF_Friends_2017="$basedir/2017/friends/FakeFactors_updated/"
TauTriggers_Friends_2017="$basedir/2017/friends/TauTriggers/"


# Samples Run2018
ARTUS_OUTPUTS_2018="$basedir/2018/ntuples/"
#NNScore_Friends_2018="$basedir/2018/friends/NNScore/"
SVFit_Friends_2018="$basedir/2018/friends/SVFit/"
MELA_Friends_2018="$basedir/2018/friends/MELA/"
FF_Friends_2018="$basedir/2018/friends/FakeFactors_updated/"
TauTriggers_Friends_2018="$basedir/2018/friends/TauTriggers/"


# ERA handling
if [[ $ERA == *"2016"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    NNScore_Friends=$NNScore_Friends_2016
    SVFit_Friends=$SVFit_Friends_2016
    MELA_Friends=$MELA_Friends_2016
    FF_Friends=$FF_Friends_2016
    TauTriggers_Friends=$TauTriggers_Friends_2016
elif [[ $ERA == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    NNScore_Friends=$NNScore_Friends_2017
    SVFit_Friends=$SVFit_Friends_2017
    MELA_Friends=$MELA_Friends_2017
    FF_Friends=$FF_Friends_2017
    TauTriggers_Friends=$TauTriggers_Friends_2017
elif [[ $ERA == *"2018"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2018
    NNScore_Friends=$NNScore_Friends_2018
    SVFit_Friends=$SVFit_Friends_2018
    MELA_Friends=$MELA_Friends_2018
    FF_Friends=$FF_Friends_2018
    TauTriggers_Friends=$TauTriggers_Friends_2018
fi

### check if there are valid local friend trees and, if yes overwrite the friend tree directory with the local ones
if [[ -d output/friend_trees ]]; then
    DIR=${WD}/output/friend_trees/$ERA/nnscore_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && NNScore_Friends=$DIR
    DIR=${WD}/output/friend_trees/$ERA/svfit_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && SVFit_Friends=$DIR
    DIR=${WD}/output/friend_trees/$ERA/mela_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && MELA_Friends=$DIR
    DIR=${WD}/output/friend_trees/$ERA/ff_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && FF_Friends=$DIR
fi

### channels specific friend tree.
# Used for example to process the event channel without including the fakefactor friends
ARTUS_FRIENDS_EM="$NNScore_Friends $SVFit_Friends $MELA_Friends"
ARTUS_FRIENDS_ET="$NNScore_Friends $SVFit_Friends $MELA_Friends $TauTriggers_Friends"
ARTUS_FRIENDS_MT="$NNScore_Friends $SVFit_Friends $MELA_Friends $TauTriggers_Friends"
ARTUS_FRIENDS_TT="$NNScore_Friends $SVFit_Friends $MELA_Friends $TauTriggers_Friends"
ARTUS_FRIENDS="$NNScore_Friends $SVFit_Friends $MELA_Friends"
ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends

### for "backwards compability". Should be removed at some point. DO not use these variables

ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends
ARTUS_FRIENDS_FAKE_FACTOR_INCL=$FF_Friends
ARTUS_FRIENDS_FAKE_FACTOR_2016=$FF_Friends_2016
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016=$ARTUS_FRIENDS_FAKE_FACTOR_2016
ARTUS_FRIENDS_FAKE_FACTOR_2017=$FF_Friends_2017
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=$FF_Friends_2017
ARTUS_FRIENDS_FAKE_FACTOR_2018=$FF_Friends_2018
ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018=$FF_Friends_2018
ARTUS_OUTPUTS_EM_2017=""

ARTUS_FRIENDS_2016="$NNScore_Friends_2016 $SVFit_Friends_2016 $MELA_Friends_2016" # TODO update once friends are produced
ARTUS_FRIENDS_ET_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_MT_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_TT_2016=$ARTUS_FRIENDS_2016
ARTUS_FRIENDS_EM_2016=$ARTUS_FRIENDS_2016


ARTUS_FRIENDS_2017="$NNScore_Friends_2017 $SVFit_Friends_2017 $MELA_Friends_2017"
ARTUS_FRIENDS_ET_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_MT_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_TT_2017=$ARTUS_FRIENDS_2017
ARTUS_FRIENDS_EM_2017=$ARTUS_FRIENDS_2017


ARTUS_FRIENDS_2018="$SVFit_Friends_2018 $MELA_Friends_2018 $NNScore_Friends_2018"
ARTUS_FRIENDS_ET_2018=$ARTUS_FRIENDS_2018
ARTUS_FRIENDS_MT_2018=$ARTUS_FRIENDS_2018
ARTUS_FRIENDS_TT_2018=$ARTUS_FRIENDS_2018
ARTUS_FRIENDS_EM_2018=$ARTUS_FRIENDS_2018
