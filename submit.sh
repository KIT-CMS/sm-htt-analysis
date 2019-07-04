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

cd CMSSW_10_2_14/src/NNScore_workdir/

condor_submit condor_NNScore_resubmit.jdl