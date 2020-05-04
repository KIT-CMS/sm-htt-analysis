#!/bin/bash

### Setup of CMSSW release
CMSSW=CMSSW_10_2_16_UL

export SCRAM_ARCH=slc7_amd64_gcc700
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project $CMSSW; pushd $CMSSW/src
eval `scramv1 runtime -sh`

# combine on 102X slc7
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.0.1
cd -

# CombineHarvester (current master for 102X)
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester

# SM analysis specific code
git clone https://github.com/KIT-CMS/MSSMvsSMRun2Legacy.git CombineHarvester/MSSMvsSMRun2Legacy -b nmssm_analysis

# compile everything
# Build
CORES=`grep -c ^processor /proc/cpuinfo`
scramv1 b clean; scramv1 b -j $CORES
