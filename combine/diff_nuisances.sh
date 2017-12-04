#!/bin/bash

source utils/setup_cmssw.sh

python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -f html mlfit.root > diff_nuisances.html
