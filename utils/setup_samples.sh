#!/bin/bash
set -e

ERA=$1
TAG=$2

if [[ ! -z $3 ]]; then
    OUTPUTDIR=$3
elif [[ -d output/friend_trees ]];then
    OUTPUTDIR=$( cd output; pwd -P)
fi

# Kappa database
KAPPA_DATABASE=datasets/datasets.json

#### ERA specific part. If a sample is not available comment it out here.
# Samples Run2016
basedir="/ceph/htautau/deeptau_02-20"
ARTUS_OUTPUTS_2016="/portal/ekpbms1/home/jbechtel/postprocessing/nmssm/sm-htt-analysis/ntuples/2016/"
SVFit_Friends_2016="/portal/ekpbms1/home/jbechtel/postprocessing/nmssm/sm-htt-analysis/friends/2016/SVFit/"
FF_Friends_2016="$basedir/2016/friends/FakeFactors_final_v2/"
TauTriggers_Friends_2016="/portal/ekpbms1/home/jbechtel/postprocessing/nmssm/sm-htt-analysis/friends/2016/TauTriggers/"

# Samples Run2017
ARTUS_OUTPUTS_2017="/portal/ekpbms1/home/jbechtel/postprocessing/nmssm/sm-htt-analysis/ntuples/2017/"
SVFit_Friends_2017="$basedir/2017/friends/SVFit/"
FF_Friends_2017="$basedir/2017/friends/FakeFactors_final_v2/"
TauTriggers_Friends_2017="/portal/ekpbms1/home/jbechtel/postprocessing/nmssm/sm-htt-analysis/friends/2017/TauTriggers/" 

# Samples Run2018
ARTUS_OUTPUTS_2018="/portal/ekpbms1/home/jbechtel/postprocessing/nmssm/sm-htt-analysis/ntuples/2018/"
SVFit_Friends_2018=""
FF_Friends_2018="$basedir/2018/friends/FakeFactors_final_v2/"
TauTriggers_Friends_2018="/portal/ekpbms1/home/jbechtel/postprocessing/nmssm/sm-htt-analysis/friends/2018/TauTriggers/" 


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

ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends
ARTUS_FRIENDS_FAKE_FACTOR_2016=$FF_Friends_2016
ARTUS_FRIENDS_FAKE_FACTOR_2017=$FF_Friends_2017
ARTUS_FRIENDS_FAKE_FACTOR_2018=$FF_Friends_2018
ARTUS_OUTPUTS_EM_2017=""

ARTUS_FRIENDS_2016="$SVFit_Friends_2016 $MELA_Friends_2016" 
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
