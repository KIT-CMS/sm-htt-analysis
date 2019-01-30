#!/bin/bash

source utils/setup_cmssw.sh

ERA=$1

combine -M AsymptoticLimits \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    -m 125 -n $ERA \
    -v 1 \
    ${ERA}_workspace.root
