#!/bin/bash

#set -e # quit on error
#shopt -s checkjobs # wait for all jobs before exiting

export SCRAM_ARCH=slc6_amd64_gcc700
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

THIS_PWD=$PWD
cd /portal/ekpbms3/home/mscham/CMSSW_10_2_14/src
eval `scramv1 runtime -sh`
cd $THIS_PWD

era=$1
channel=$2
modus=$3
if [[ ! "submit check collect" =~ $modus || -z $modus ]]; then
    echo "modus must be submit or check!"
    exit 1
fi
source /home/mscham/sm-htt/utils/setup_samples.sh $era


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

# # Set stack size to unlimited, otherwise combine may throw a segfault for
# # complex fits
ulimit -s unlimited
job_management.py --executable NNScore \
                  --batch_cluster etp \
                  --command $modus \
                  --input_ntuples_directory $input_ntuples_dir  \
                  --walltime 1800  \
                  --events_per_job 200000 \
                  --friend_ntuples_directories $friendTrees \
                  --cores 50 \
                  #--restrict_to_channels "mt"
                  #--custom_workdir_path "/storage/b/sjoerger/pruning/mt/complete_analysis/18_variables" \
#
# # If command is submit:
cd /portal/ekpbms3/home/mscham/CMSSW_10_2_14/src/NNScore_workdir/
if [[ $modus == "submit" ]]; then
    condor_submit condor_NNScore_0.jdl
# elif [[ $modus=="check" ]]; then
#     condor_submit condor_NNScore_resubmit.jdl
fi
cd $THIS_PWD
