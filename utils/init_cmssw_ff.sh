#!/bin/bash

# Export CMSSW
export SCRAM_ARCH=slc6_amd64_gcc491
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scram project CMSSW CMSSW_8_0_4
cd CMSSW_8_0_4/src

git clone ssh://git@github.com/CMS-HTT/Jet2TauFakes.git HTTutilities/Jet2TauFakes
cd HTTutilities/Jet2TauFakes
git checkout v0.2.2
scram b
mkdir data
git clone ssh://git@gitlab.cern.ch:7999/cms-htt/Jet2TauFakesFiles.git data
