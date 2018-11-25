#!/bin/bash

ERAS=${@:1}

TAG=""
for ERA in ${ERAS}
do
    TAG="${TAG}${ERA}_"
done

source utils/setup_cmssw.sh

python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -f html mlfit${TAG}.root > ${TAG}diff_nuisances.html
