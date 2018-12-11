#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc491
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

THIS_PWD=$PWD
cd CMSSW_7_4_7/src
eval `scramv1 runtime -sh`
cd $THIS_PWD

# Set stack size to unlimited, otherwise combine may throw a segfault for
# complex fits
ulimit -s unlimited
