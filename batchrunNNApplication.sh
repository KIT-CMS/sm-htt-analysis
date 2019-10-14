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
export VO_CMS_SW_DIR="/cvmfs/cms.cern.ch"
source $VO_CMS_SW_DIR/cmsset_default.sh


if [[ ! "submit collect rungc delete" =~ $modus || -z $modus ]]; then
    logerror "modus must be submit or collect but is $modus !"
    exit 1
fi
if [[ ! "etp7 lxplus7 naf" =~ $cluster || -z $cluster ]]; then
    logerror "cluster must be etp7, lxplus7, but is $cluster!"
    exit 1
fi

if [[ $cluster = "etp7" ]]; then
    #### use local resources
    export sw_src_dir="/portal/ekpbms3/home/${USER}/CMSSW_10_2_14/src"
    export batch_out="/portal/ekpbms3/home/${USER}/batch-out"
    eventsPerJob=2000000
    walltime=10000
    friendTrees=${ftarray[@]}
    friendTrees="/ceph/htautau/2017/nnscore_friends/ /ceph/htautau/2017/svfit_friends/ /ceph/htautau/2017/mela_friends/"
    input_ntuples_dir="/ceph/htautau/2017/ntuples/"

elif [[ $cluster == "lxplus7" ]]; then
    eventsPerJob=200000
    walltime=3000
    case $era in
        "2016" )
            logerror No friend trees for $era on lxplus7
            exit 1
            input_ntuples_dir="/eos/user/s/sbrommer/scratch/2019_06_13"
            ;;
        "2017" )
            input_ntuples_dir="/eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis"
            friendTrees="/eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis_MELA/MELA_collected /eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis_SVFit/SVFit_collected"
            input_ntuples_dir="/eos/user/m/mscham/htautau/2017/ntuples"
            friendTrees="/eos/user/m/mscham/htautau/2017/ff_friends /eos/user/m/mscham/htautau/2017/mela_friends /eos/user/m/mscham/htautau/2017/svfit_friends"
            ;;
        "2018" )
            input_ntuples_dir="/eos/user/m/mscham/htautau/2018/ntuples"
            friendTrees="/eos/user/m/mscham/htautau/2018/ff_friends /eos/user/m/mscham/htautau/2018/mela_friends /eos/user/m/mscham/htautau/2018/svfit_friends"
            ;;
    esac
    export remote="cern"
    export streamext="--extended_file_access root://eosuser.cern.ch/"
    export sw_src_dir="/afs/cern.ch/user/${USER::1}/${USER}/CMSSW_10_2_14/src"
    export batch_out="/afs/cern.ch/work/${USER::1}/${USER}/batch-out"
elif [[ $cluster == "naf" ]]; then
    eventsPerJob=2000000
    walltime=1000
    case $era in
        "2016" )
            logerror No friend trees for $era on lxplus7
            exit 1
            input_ntuples_dir="/nfs/dust/cms/group/higgs-kit/ekp/ARTUS_OUTPUTS_2016"
            friendTrees="/nfs/dust/cms/group/higgs-kit/ekp/FF_Friends_2016"
            ;;
        "2017" )
            input_ntuples_dir="/nfs/dust/cms/group/higgs-kit/ekp/ARTUS_OUTPUTS_2017"
            friendTrees="/nfs/dust/cms/group/higgs-kit/ekp/FF_Friends_2017 /nfs/dust/cms/group/higgs-kit/ekp/MELA_Friends_2017 /nfs/dust/cms/group/higgs-kit/ekp/SVFit_Friends_2017"
            ;;
        "2018" )
            input_ntuples_dir="/nfs/dust/cms/user/jbechtel/htautau/analysis_ntuples_2"
            friendTrees="/nfs/dust/cms/user/mscham/ff_friends_2018 /nfs/dust/cms/user/jbechtel/htautau/analysis_friends_mela /nfs/dust/cms/user/jbechtel/htautau/analysis_friends_sv"
            ;;
    esac
    export remote="naf"
    export sw_src_dir="/afs/desy.de/user/m/mscham/CMSSW_10_2_14/src"
    export batch_out="/nfs/dust/cms/user/mscham/NNScoreApp"
fi
export workdir=$batch_out/$outdir
export submitlock=$workdir/$era-$2.lock
echo "run this on $cluster"
tmp=$( mktemp )
cat << eof > $tmp
set -e
source /cvmfs/cms.cern.ch/cmsset_default.sh
THIS_PWD=\$PWD
cd $sw_src_dir
eval \`scramv1 runtime -sh\`
export PATH=\$PATH:\$PWD/grid-control:\$PWD/grid-control/scripts
cd -
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
job_management.py --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $input_ntuples_dir  \\
                  --walltime $walltime  \\
                  --events_per_job $eventsPerJob \\
                  --friend_ntuples_directories $friendTrees \\
                  --cores 5 \\
                  --restrict_to_channels $channels \\
                  --custom_workdir_path $workdir && touch $submitlock
else
echo Skipping submission, because $submitlock exists
fi
fi


if [[ $modus == rungc ]]; then
export X509_USER_PROXY=~/.globus/x509up
voms-proxy-info
go.py $workdir/NNScore_workdir/grid_control_NNScore.conf -Gc -m 20
fi


if [[ "collect" == $modus ]]; then
job_management.py --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $input_ntuples_dir  \\
                  --walltime $walltime  \\
                  --events_per_job $eventsPerJob \\
                  --friend_ntuples_directories $friendTrees \\
                  --cores 5 \\
                  --restrict_to_channels $channels \\
                  --custom_workdir_path $workdir
fi

if [[ $modus == delete ]]; then
rm -r $workdir
fi

eof

if [[ $cluster == "etp7" ]]; then
    cat $tmp | bash
else
    loginfo "$cluster is executing:"
    alogrun $remote $tmp
fi
