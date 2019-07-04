#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc700
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

THIS_PWD=$PWD
cd /portal/ekpbms2/home/sjoerger/sm-htt-analysis/CMSSW_10_2_14/src
eval `scramv1 runtime -sh`
cd $THIS_PWD

# Set stack size to unlimited, otherwise combine may throw a segfault for
# complex fits
ulimit -s unlimited

job_management.py --executable NNScore \
                  --batch_cluster lxplus \
                  --command submit \
                  --input_ntuples_directory "/storage/b/akhmet/merged_files_from_naf/Full_2017_test_all-channels/" \
                  --walltime 1800  \
                  --events_per_job 200000 \
                  --friend_ntuples_directories "/storage/b/akhmet/merged_files_from_naf/SVFit_collected/" "/storage/b/akhmet/merged_files_from_naf/MELA_collected/" \
                  --cores 50 \
                  #--restrict_to_channels "mt"
                  #--custom_workdir_path "/storage/b/sjoerger/pruning/mt/complete_analysis/18_variables" \

#NNScore --input_friends /storage/b/akhmet/merged_files_from_naf/SVFit_collected/W2JetsToLNu_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_v4/W2JetsToLNu_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_v4.root /storage/b/akhmet/merged_files_from_naf/MELA_collected/W2JetsToLNu_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_v4/W2JetsToLNu_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_v4.root --tree ntuple --last_entry 23223 --first_entry 0 --input /storage/b/akhmet/merged_files_from_naf/Full_2017_test_all-channels/W2JetsToLNu_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_v4/W2JetsToLNu_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_v4.root --folder mt_btagMistagDown

cd CMSSW_10_2_14/src/NNScore_workdir/

condor_submit condor_NNScore_0.jdl

#cd CMSSW_10_2_14/src/NNScore_workdir
#condor_submit condor_NNScore_resubmit.jdl
