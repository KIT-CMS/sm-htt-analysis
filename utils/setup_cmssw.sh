#!/bin/bash

export SCRAM_ARCH=slc7_amd64_gcc700
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

THIS_PWD=$PWD
cd CMSSW_10_2_16_UL/src
eval `scramv1 runtime -sh`
cd $THIS_PWD

# Set stack size to unlimited, otherwise combine may throw a segfault for
# complex fits
ulimit -s unlimited
