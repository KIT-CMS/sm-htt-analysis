#!/bin/bash
set -e # quit on error
shopt -s checkjobs # wait for all jobs before exiting

era=$1
channels=$( echo $2 | tr "," " " )
cluster=$3
modus=$4
tag=$5
outdir=${era}_${tag}
source utils/bashFunctionCollection.sh
#export SCRAM_ARCH="slc6_amd64_gcc700"

if [[ ! "submit collect rungc delete" =~ $modus || -z $modus ]]; then
    logerror "modus must be submit or collect but is $modus !"
    exit 1
fi
if [[ ! "etp7 lxplus7 naf" =~ $cluster || -z $cluster ]]; then
    logerror "cluster must be etp7, lxplus7 or naf, but is $cluster!"
    exit 1
fi

if [[ $cluster = "etp7" ]]; then
    #### use local resources
    export sw_src_dir="/portal/ekpbms3/home/${USER}/CMSSW_10_2_14/src"
    export batch_out="/portal/ekpbms3/home/${USER}/batch-out"
    source utils/setup_samples.sh $era $tag
    eventsPerJob=2000000
    walltime=10000
elif [[ $cluster == "lxplus7" ]]; then
    export remote="cern"
    export streamext="--extended_file_access root://eosuser.cern.ch/"
    export sw_src_dir="/afs/cern.ch/user/${USER::1}/${USER}/CMSSW_10_2_14/src"
    export batch_out="/afs/cern.ch/work/${USER::1}/${USER}/batch-out"
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
            ARTUS_OUTPUTS="/eos/user/m/mscham/htautau/2017/ntuples"
            ARTUS_FRIENDS="/eos/user/m/mscham/htautau/2017/ff_friends /eos/user/m/mscham/htautau/2017/mela_friends /eos/user/m/mscham/htautau/2017/svfit_friends"
            ;;
        "2018" )
            ARTUS_OUTPUTS="/eos/user/m/mscham/htautau/2018/ntuples"
            ARTUS_FRIENDS="/eos/user/m/mscham/htautau/2018/ff_friends /eos/user/m/mscham/htautau/2018/mela_friends /eos/user/m/mscham/htautau/2018/svfit_friends"
            ;;
    esac
elif [[ $cluster == "naf" ]]; then
    export remote="naf"
    export sw_src_dir="/afs/desy.de/user/m/mscham/CMSSW_10_2_14/src"
    export batch_out="/nfs/dust/cms/user/mscham/NNScoreApp"
    eventsPerJob=2000000
    walltime=2000
    ARTUS_OUTPUTS="/nfs/dust/cms/group/higgs-kit/ekp/deeptau/$era/ntuples"
    ARTUS_FRIENDS="/nfs/dust/cms/group/higgs-kit/ekp/deeptau/$era/friends/FakeFactors /nfs/dust/cms/group/higgs-kit/ekp/deeptau/$era/friends/MELA /nfs/dust/cms/group/higgs-kit/ekp/deeptau/$era/friends/SVFit"
fi

export workdir=$batch_out/$outdir
export submitlock=$workdir/$era-$2.lock
export jm=$sw_src_dir/HiggsAnalysis/friend-tree-producer/scripts/job_management.py

set -x
echo "run this on $cluster"
tmp=$( mktemp )
cat << eof > $tmp
set -e
source /cvmfs/cms.cern.ch/cmsset_default.sh
pushd $sw_src_dir
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

if [[ "submit" == $modus ]]; then
if [[ ! -f $submitlock ]]; then
$jm --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $ARTUS_OUTPUTS  \\
                  --walltime $walltime  \\
                  --events_per_job $eventsPerJob \\
                  --friend_ntuples_directories $ARTUS_FRIENDS \\
                  --cores 5 \\
                  --restrict_to_channels $channels \\
                  --custom_workdir_path $workdir && touch $submitlock
else
echo Skipping submission, because $submitlock exists
fi
fi


if [[ "rungc" == $modus ]]; then
export X509_USER_PROXY=~/.globus/x509up
voms-proxy-info
go.py $workdir/NNScore_workdir/grid_control_NNScore.conf -Gc -m 10
fi


if [[ "collect" == $modus ]]; then
$jm --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $ARTUS_OUTPUTS  \\
                  --walltime $walltime  \\
                  --events_per_job $eventsPerJob \\
                  --friend_ntuples_directories $ARTUS_FRIENDS \\
                  --cores 5 \\
                  --restrict_to_channels $channels \\
                  --custom_workdir_path $workdir
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
