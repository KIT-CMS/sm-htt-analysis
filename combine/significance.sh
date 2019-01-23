#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# NOTE: toysFrequentist computes postfit signifiance
combine -M ProfileLikelihood \
    -t -1 --expectSignal 1 \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --significance \
    -m 125 -n $ERA \
    --toysFrequentist \
    -v 1 \
    ${ERA}_workspace.root
