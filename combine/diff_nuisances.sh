#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -f html mlfit${ERA}.root > ${ERA}_diff_nuisances.html
