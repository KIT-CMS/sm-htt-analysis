#!/bin/bash
set -e # quit on error
shopt -s checkjobs # wait for all jobs before exiting

era=$1
channels=$( echo $2 | tr "," " " )
modus=$3
tag=$4
all_eras=$5
outdir=${era}_${tag}
source utils/bashFunctionCollection.sh
## set the user specific paths (cluster, remote, batch_out, cmssw_src)
source .userconfig

if [[ $all_eras == 1 ]]; then
  echo "Using conditional training!"
fi

if [[ ! "submit collect rungc delete" =~ $modus || -z $modus ]]; then
    logerror "modus must be submit or collect but is $modus !"
    exit 1
fi
if [[ ! "etp7 lxplus7 naf7" =~ $cluster || -z $cluster ]]; then
    logerror "cluster must be etp7, lxplus7 or naf7, but is $cluster!"
    exit 1
fi

if [[ $cluster = "etp7" ]]; then
    source utils/setup_samples.sh $era $tag
    ARTUS_FRIENDS="$SVFit_Friends $MELA_Friends $FF_Friends"
    eventsPerJob=2000000
    walltime=10000
elif [[ $cluster == "lxplus7" ]]; then
    export streamext="--extended_file_access root://eosuser.cern.ch/"
    eventsPerJob=200000
    walltime=3000
    case $era in
        "2016" )
            logerror No friend trees for $era on lxplus7
            exit 1
            ARTUS_OUTPUTS="/eos/user/s/sbrommer/scratch/2019_06_13"
            ;;
        "2017" )
            ARTUS_OUTPUTS="/eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis"
            ARTUS_FRIENDS="/eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis_MELA/MELA_collected /eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis_SVFit/SVFit_collected"
            ARTUS_OUTPUTS="/eos/user/${USER::1}/${USER}/htautau/2017/ntuples"
            ARTUS_FRIENDS="/eos/user/${USER::1}/${USER}/htautau/2017/ff_friends /eos/user/${USER::1}/${USER}/htautau/2017/mela_friends /eos/user/${USER::1}/${USER}/htautau/2017/svfit_friends"
            ;;
        "2018" )
            ARTUS_OUTPUTS="/eos/user/${USER::1}/${USER}/htautau/2018/ntuples"
            ARTUS_FRIENDS="/eos/user/${USER::1}/${USER}/htautau/2018/ff_friends /eos/user/${USER::1}/${USER}/htautau/2018/mela_friends /eos/user/${USER::1}/${USER}/htautau/2018/svfit_friends"
            ;;
    esac
elif [[ $cluster == "naf7" ]]; then
    eventsPerJob=2000000
    walltime=2000
    ARTUS_OUTPUTS="/nfs/dust/cms/group/higgs-kit/ekp/deeptau_eoy/$era/ntuples"
    ARTUS_FRIENDS="/nfs/dust/cms/group/higgs-kit/ekp/deeptau_eoy/$era/friends/FakeFactors /nfs/dust/cms/group/higgs-kit/ekp/deeptau_eoy/$era/friends/MELA /nfs/dust/cms/group/higgs-kit/ekp/deeptau_eoy/$era/friends/SVFit"
fi

export workdir=$batch_out/$outdir
export submitlock=$workdir/$era-$2.submit.lock
export collectlock=$workdir/$era-$2.collect.lock
export jm=$cmssw_src/HiggsAnalysis/friend-tree-producer/scripts/job_management.py

echo "run this on $cluster"
tmp=$( mktemp )
cat << eof > $tmp
hostname
source /cvmfs/cms.cern.ch/cmsset_default.sh
set -e
pushd $cmssw_src
eval \`scramv1 runtime -sh\`
export PATH=\$PATH:\$PWD/grid-control:\$PWD/grid-control/scripts
popd
echo This should be the CMSSW_BASE:
echo \$CMSSW_BASE

set -x
# # Set stack size to unlimited, otherwise combine may throw a segfault for
# # complex fits

ulimit -s unlimited

if [[ ! -d $workdir ]]; then
mkdir -p $workdir
fi

if [[ "submit" == $modus && ! -f $submitlock  ]]; then
if [[ $all_eras == 1 ]]; then
echo Executing with conditional argument
$jm --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $ARTUS_OUTPUTS  \\
                  --walltime $walltime  \\
                  --events_per_job $eventsPerJob \\
                  --friend_ntuples_directories $ARTUS_FRIENDS \\
                  --extra-parameters "--lwtnn_config \$CMSSW_BASE/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/$tag" \\
                  --cores 6 \\
                  --restrict_to_channels $channels \\
                  --conditional 1 \\
                  --custom_workdir_path $workdir && touch $submitlock

else
echo Executing without conditional argument
$jm --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $ARTUS_OUTPUTS  \\
                  --walltime $walltime  \\
                  --events_per_job $eventsPerJob \\
                  --friend_ntuples_directories $ARTUS_FRIENDS \\
                  --extra-parameters "--lwtnn_config \$CMSSW_BASE/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/$tag" \\
                  --cores 6 \\
                  --restrict_to_channels $channels \\
                  --custom_workdir_path $workdir && touch $submitlock
fi
else
echo Skipping submission, because $submitlock exists
fi


if [[ "rungc" == $modus ]]; then
export X509_USER_PROXY=~/.globus/x509up
voms-proxy-info
go.py $workdir/NNScore_workdir/grid_control_NNScore.conf -Gc -m 15
fi


if [[ "collect" == $modus && ! -f $collectlock  ]]; then
$jm --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $ARTUS_OUTPUTS  \\
                  --walltime $walltime  \\
                  --events_per_job $eventsPerJob \\
                  --friend_ntuples_directories $ARTUS_FRIENDS \\
                  --cores 4 \\
                  --restrict_to_channels $channels \\
                  --custom_workdir_path $workdir && touch $collectlock
fi

if [[ "delete" == $modus ]]; then
rm -r $workdir
fi
eof


if [[ $cluster == "etp7" ]]; then
    cat $tmp | bash
else
    loginfo "$cluster is executing:"
    alogrun $remote $tmp
fi
