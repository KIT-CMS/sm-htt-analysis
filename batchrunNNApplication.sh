#!/bin/bash
set -e # quit on error
shopt -s checkjobs # wait for all jobs before exiting

era=$1
channels=$( echo $2 | tr "," " " )
cluster=$3
modus=$4
outdir=$5

source utils/bashFunctionCollection.sh
#export SCRAM_ARCH="slc6_amd64_gcc700"
export VO_CMS_SW_DIR="/cvmfs/cms.cern.ch"
source $VO_CMS_SW_DIR/cmsset_default.sh
export sm_htt_analysis_dir="/portal/ekpbms3/home/${USER}/sm-htt-analysis"


if [[ ! "submit check" =~ $modus || -z $modus ]]; then
    logerror "modus must be submit or check but is $modus !"
    exit 1
fi
if [[ ! "etp lxplus7" =~ $cluster || -z $cluster ]]; then
    logerror "cluster must be etp, lxplus7, but is $cluster!"
    exit 1
fi

if [[ $cluster = "etp" ]]; then
    #### use local resources
    export sw_src_dir="/portal/ekpbms3/home/${USER}/CMSSW_10_2_14/src"
    export batch_out="/portal/ekpbms3/home/${USER}/batch-out"

    #### Path pick ntuples + friend tree paths here
    source $sm_htt_analysis_dir/utils/setup_samples.sh $era
    input_ntuples_dir=$ARTUS_OUTPUTS

    if [[ $channel != "" ]]; then
        name=ARTUS_FRIENDS_${channel}_${era}
        friendTrees=${!name}
    else
        name=ARTUS_FRIENDS_EM_${era}
        friendTrees=${!name}
    fi
    ##Remove NNscores from list of friendTrees
    echo $NNScore
    read -a ftarray <<< $friendTrees
    for (( i = 0; i < ${#ftarray[@]}; i++ )); do
        if [[ ${ftarray[$i]} == $NNScore ]]; then
            echo removing ftarray[${i}]
            unset 'ftarray[${i}]'
        fi
    done
    friendTrees=${ftarray[@]}

elif [[ $cluster == "lxplus7" ]]; then
    case $era in
        "2016" )
            logerror No friend trees for $era on lxplus7
            exit 1
            input_ntuples_dir="/eos/user/s/sbrommer/scratch/2019_06_13"
            ;;
        "2017" )
            input_ntuples_dir="/eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis"
            friendTrees="/eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis_MELA/MELA_collected /eos/user/a/aakhmets/merged_ntuples/07-06-2019_full_analysis_SVFit/SVFit_collected"
            ;;
        "2018" )
            logerror No ntuples for $era on lxplus7
            exit 1
            ;;
    esac

    export sw_src_dir="/afs/cern.ch/user/${USER::1}/${USER}/CMSSW_10_2_14/src"
    export batch_out="/afs/cern.ch/work/${USER::1}/${USER}/batch-out"
fi
export workdir=$batch_out/$outdir


set -x
echo "run this on $cluster"
tmp=$( mktemp )
cat << eof > $tmp
set -e
if [[ ! -d $workdir ]]; then
    mkdir -p $workdir
fi

THIS_PWD=\$PWD
cd $sw_src_dir
eval \`scramv1 runtime -sh\`
cd -
echo This should be the CMSSW_BASE:
echo \$CMSSW_BASE
set -x
if [[ $modus == submit ]]; then
    rm -r $workdir
    mkdir $workdir

fi

# # Set stack size to unlimited, otherwise combine may throw a segfault for
# # complex fits

ulimit -s unlimited

job_management.py --executable NNScore \\
                  --batch_cluster $cluster \\
                  --command $modus \\
                  --input_ntuples_directory $input_ntuples_dir  \\
                  --walltime 600  \\
                  --events_per_job 200000 \\
                  --friend_ntuples_directories $friendTrees \\
                  --cores 5 \\
                  --restrict_to_channels $channels \\
                  --custom_workdir_path $workdir

cd $workdir/NNScore_workdir/
if [[ $modus == submit ]]; then
    condor_submit condor_NNScore_0.jdl
elif [[ $modus == "check" ]]; then
    cat arguments_resubmit.txt
    condor_submit condor_NNScore_resubmit.jdl
    if [[ "0" == \`cat arguments_resubmit.txt | wc -l\` ]]; then
        job_management.py --executable NNScore \\
            --batch_cluster $cluster \\
            --command collect \\
            --input_ntuples_directory $input_ntuples_dir  \\
            --walltime 600  \\
            --events_per_job 200000 \\
            --friend_ntuples_directories $friendTrees \\
            --cores 5 \\
            --restrict_to_channels $channels \\
            --custom_workdir_path $workdir
    fi
fi

eof


if [[ $cluster == etp ]]; then
    cat $tmp | bash
elif [[ $cluster == lxplus7 ]]; then
    loginfo "lxplus7 is executing:"
    lxrun $tmp
    #echo "Execute before submiting: cd $sw_src_dir; eval \`scramv1 runtime -sh\`; cd -"
fi

# # If command is submit:
# echo On lxplus7 :
# echo "cd $sw_src_dir; eval \`scramv1 runtime -sh\` ; cd - "
# if [[ $modus == "submit" ]]; then
#     echo condor_submit NNScore_workdir/condor_NNScore_0.jdl
# elif [[ $modus=="check" ]]; then
#     echo condor_submit condor_NNScore_resubmit.jdl
# fi



###rsync -avhP /afs/cern.ch/work/${USER::1}/${USER}/batch-out /eos/user/${USER::1}/${USER}/batch-out/
