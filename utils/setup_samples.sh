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
export KAPPA_DATABASE=datasets/datasets.json

#### ERA specific part. If a sample is not available comment it out here.
# Samples Run2016
export basedir="/ceph/mscham/deeptau_eoy"
export ARTUS_OUTPUTS_2016="$basedir/2016/ntuples/"
export NNScore_Friends_2016="$basedir/2016/friends/NNScore/emb_ff_stage1_fix/"
export SVFit_Friends_2016="$basedir/2016/friends/SVFit/"
export MELA_Friends_2016="$basedir/2016/friends/MELA/"
export FF_Friends_2016="$basedir/2016/friends/FakeFactors_updated/"
export TauTriggers_Friends_2016="$basedir/2016/friends/TauTriggers/"

# Samples Run2017
export ARTUS_OUTPUTS_2017="$basedir/2017/ntuples/"
export NNScore_Friends_2017="$basedir/2017/friends/NNScore/emb_ff_stage1_fix/"
export SVFit_Friends_2017="$basedir/2017/friends/SVFit/"
export MELA_Friends_2017="$basedir/2017/friends/MELA/"
export FF_Friends_2017="$basedir/2017/friends/FakeFactors_updated/"
export TauTriggers_Friends_2017="$basedir/2017/friends/TauTriggers/"

# Samples Run2018
export ARTUS_OUTPUTS_2018="$basedir/2018/ntuples/"
export NNScore_Friends_2018="$basedir/2018/friends/NNScore/emb_ff_stage1_fix/"
export SVFit_Friends_2018="$basedir/2018/friends/SVFit/"
export MELA_Friends_2018="$basedir/2018/friends/MELA/"
export FF_Friends_2018="$basedir/2018/friends/FakeFactors_updated/"
export TauTriggers_Friends_2018="$basedir/2018/friends/TauTriggers/"


# ERA handling
if [[ $ERA == *"2016"* ]]
then
    export ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    export NNScore_Friends=$NNScore_Friends_2016
    export SVFit_Friends=$SVFit_Friends_2016
    export MELA_Friends=$MELA_Friends_2016
    export FF_Friends=$FF_Friends_2016
    export TauTriggers_Friends=$TauTriggers_Friends_2016
elif [[ $ERA == *"2017"* ]]
then
    export ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    export NNScore_Friends=$NNScore_Friends_2017
    export SVFit_Friends=$SVFit_Friends_2017
    export MELA_Friends=$MELA_Friends_2017
    export FF_Friends=$FF_Friends_2017
    export TauTriggers_Friends=$TauTriggers_Friends_2017
elif [[ $ERA == *"2018"* ]]
then
    export ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2018
    export NNScore_Friends=$NNScore_Friends_2018
    export SVFit_Friends=$SVFit_Friends_2018
    export MELA_Friends=$MELA_Friends_2018
    export FF_Friends=$FF_Friends_2018
    export TauTriggers_Friends=$TauTriggers_Friends_2018
fi

### check if there are valid local friend trees and, if yes overwrite the friend tree directory with the local ones
if [[ ! -z $OUTPUTDIR && -d $OUTPUTDIR ]]; then
    export DIR=${OUTPUTDIR}/friend_trees/$ERA/nnscore_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && export NNScore_Friends=$DIR
    export DIR=${OUTPUTDIR}/friend_trees/$ERA/svfit_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && export SVFit_Friends=$DIR
    export DIR=${OUTPUTDIR}/friend_trees/$ERA/mela_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && export MELA_Friends=$DIR
    export DIR=${OUTPUTDIR}/friend_trees/$ERA/ff_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && export FF_Friends=$DIR
    export DIR=${OUTPUTDIR}/friend_trees/$ERA/tautrigger_friends/${TAG}/ && [[ -d $DIR && $(ls -A $DIR | wc -l ) -gt 5 ]] && export TauTriggers_Friends=$DIR
fi

### channels specific friend tree.
# Used for example to process the event channel without including the fakefactor friends
export ARTUS_FRIENDS_EM="$NNScore_Friends $SVFit_Friends $MELA_Friends"
export ARTUS_FRIENDS_ET="$NNScore_Friends $SVFit_Friends $MELA_Friends $TauTriggers_Friends"
export ARTUS_FRIENDS_MT="$NNScore_Friends $SVFit_Friends $MELA_Friends $TauTriggers_Friends"
export ARTUS_FRIENDS_TT="$NNScore_Friends $SVFit_Friends $MELA_Friends $TauTriggers_Friends"
export ARTUS_FRIENDS="$NNScore_Friends $SVFit_Friends $MELA_Friends  $TauTriggers_Friends"
export ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends

### for "backwards compability". Should be removed at some point. DO not use these variables

export ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends
export ARTUS_FRIENDS_FAKE_FACTOR_INCL=$FF_Friends
export ARTUS_FRIENDS_FAKE_FACTOR_2016=$FF_Friends_2016
export ARTUS_FRIENDS_FAKE_FACTOR_INCL_2016=$ARTUS_FRIENDS_FAKE_FACTOR_2016
export ARTUS_FRIENDS_FAKE_FACTOR_2017=$FF_Friends_2017
export ARTUS_FRIENDS_FAKE_FACTOR_INCL_2017=$FF_Friends_2017
export ARTUS_FRIENDS_FAKE_FACTOR_2018=$FF_Friends_2018
export ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018=$FF_Friends_2018
export ARTUS_OUTPUTS_EM_2017=""

export ARTUS_FRIENDS_2016="$NNScore_Friends_2016 $SVFit_Friends_2016 $MELA_Friends_2016" # TODO update once friends are produced
export ARTUS_FRIENDS_ET_2016=$ARTUS_FRIENDS_2016
export ARTUS_FRIENDS_MT_2016=$ARTUS_FRIENDS_2016
export ARTUS_FRIENDS_TT_2016=$ARTUS_FRIENDS_2016
export ARTUS_FRIENDS_EM_2016=$ARTUS_FRIENDS_2016


export ARTUS_FRIENDS_2017="$NNScore_Friends_2017 $SVFit_Friends_2017 $MELA_Friends_2017"
export ARTUS_FRIENDS_ET_2017=$ARTUS_FRIENDS_2017
export ARTUS_FRIENDS_MT_2017=$ARTUS_FRIENDS_2017
export ARTUS_FRIENDS_TT_2017=$ARTUS_FRIENDS_2017
export ARTUS_FRIENDS_EM_2017=$ARTUS_FRIENDS_2017


export ARTUS_FRIENDS_2018="$SVFit_Friends_2018 $MELA_Friends_2018 $NNScore_Friends_2018"
export ARTUS_FRIENDS_ET_2018=$ARTUS_FRIENDS_2018
export ARTUS_FRIENDS_MT_2018=$ARTUS_FRIENDS_2018
export ARTUS_FRIENDS_TT_2018=$ARTUS_FRIENDS_2018
export ARTUS_FRIENDS_EM_2018=$ARTUS_FRIENDS_2018
