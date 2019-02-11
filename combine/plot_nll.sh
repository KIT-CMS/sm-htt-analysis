#!/bin/bash

ERA=$1
POI=$2
NUM=$3
MIN=$4
MAX=$5

source utils/setup_cmssw.sh

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

# Perform scan
combineTool.py -M MultiDimFit -d ${ERA}_workspace.root -m 125 \
    --algo grid \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    -P ${POI} \
    --floatOtherPOIs 1 \
    --points $NUM \
    --rMin $MIN --rMax $MAX \
    -n ${ERA}_${POI}

# Plot 2*deltaNLL vs POI
python combine/plot1DScan.py \
    --main higgsCombine${ERA}_${POI}.MultiDimFit.mH125.root \
    --POI $POI \
    --output ${ERA}_${POI}_plot_nll \
    --translate combine/translate.json
