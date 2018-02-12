#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc491
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW CMSSW_7_4_7
cd CMSSW_7_4_7/src

git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit -b 74x-root6
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester -b analysis-HIG-16-006-freeze-080416

scramv1 b -j 24
scramv1 b python
