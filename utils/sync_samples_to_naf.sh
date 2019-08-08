#!/bin/bash
set +x

basedir="/ceph/htautau"
basedir_naf="/nfs/dust/cms/group/higgs-kit/ekp"


flag=0
while getopts 'r' opt; do
    case $opt in
        r) flag=1 ;;
        *) echo 'Error in command line parsing' >&2
           echo "$opt" $flag
           exit 1
    esac
done
shift "$(( OPTIND - 1 ))"

if [[ $# -eq 0 ]] ; then
    username=${USER}
else
    username=$1
fi
declare -A samples=(
    ["ARTUS_OUTPUTS_2016"]="/ceph/sbrommer/artus_ntuple/2016_samples/2019_07_19_merged/"
    ["FF_Friends_2016"]="/ceph/sbrommer/artus_ntuple/2016_samples/2019_07_19_FakeFactorFriends/FakeFactors_collected/"
    ["ARTUS_FRIENDS_2016"]=""
    ["ARTUS_OUTPUTS_2017"]="$basedir/2017/ntuples/"
    ["NNScore_Friends_2017"]=""
    ["SVFit_Friends_2017"]=""
    ["MELA_Friends_2017"]=""
    ["FF_Friends_2017"]="$basedir/2017/ff_friends/"
    ["ARTUS_OUTPUTS_EM_2017"]=""
    ["ARTUS_OUTPUTS_2018"]="$basedir/2018/ntuples/"
    ["ARTUS_FRIENDS_ET_2018"]=""
    ["ARTUS_FRIENDS_MT_2018"]=""
    ["ARTUS_FRIENDS_TT_2018"]=""
    ["ARTUS_FRIENDS_FAKE_FACTOR_2018"]=""
    ["ARTUS_FRIENDS_FAKE_FACTOR_INCL_2018"]=""
    ["SVFit_Friends_2018"]=""
    ["MELA_Friends_2018"]=""
    ["FF_Friends_2018"]="$basedir/2018/ff_friends/"
    ["NNScore_Friends_2017"]="$basedir/2017/nnscore_friends/"
    ["MELA_Friends_2017"]="$basedir/2017/mela_friends/"
    ["MELA_Friends_2018"]="$basedir/2018/mela_friends/"
    ["SVFit_Friends_2017"]="$basedir/2017/svfit_friends/"
    ["SVFit_Friends_2018"]="$basedir/2018/svfit_friends/"
)


for key in "${!samples[@]}"
do
    if [ ! -z "${samples[$key]}" ]
    then
        if [[ `hostname` == *naf* ]] ; then
            if [[ flag -eq 1 ]] ; then
                echo "rsync --progress -avzh ${username}@bms1.etp.kit.edu:${samples[$key]} $basedir_naf/$key"
                rsync --progress -avzh ${username}@bms1.etp.kit.edu:${samples[$key]} $basedir_naf/$key
            else
                echo "rsync --progress -avzhn ${username}@bms1.etp.kit.edu:${samples[$key]} $basedir_naf/$key"
                rsync --progress -avzhn ${username}@bms1.etp.kit.edu:${samples[$key]} $basedir_naf/$key
            fi
        elif  uname -a | grep -E 'bms1|sg0|sm0|ekpdeepthought' -q  ; then
            if [[ flag -eq 1 ]] ; then
                echo "rsync --progress -avzh ${samples[$key]} ${username}@naf-cms.desy.de:$basedir_naf/$key"
                rsync --progress -avzh ${samples[$key]} ${username}@naf-cms.desy.de:$basedir_naf/$key
            else
                echo "rsync --progress -avzhn ${samples[$key]} ${username}@naf-cms.desy.de:$basedir_naf/$key"
                rsync --progress -avzhn ${samples[$key]} ${username}@naf-cms.desy.de:$basedir_naf/$key
            fi
        else
            echo 'unknown host'
            exit 1
        fi
    else
        echo "Nothing set to sync for: " $key
    fi
done
