#!/bin/bash

# Export CMSSW
export SCRAM_ARCH=slc6_amd64_gcc530
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scram project CMSSW CMSSW_8_1_0
cd CMSSW_8_1_0/src

# Clone combine
git clone ssh://git@github.com/cms-analysis/HiggsAnalysis-CombinedLimit HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v7.0.12
cd ../..

# Clone CombineHarvester
git clone ssh://git@github.com/KIT-CMS/CombineHarvester CombineHarvester -b SMHTT2017-dev
mkdir -p CombineHarvester/HTTSM2017/shapes

# Build
scram b -j 24
scram b python
