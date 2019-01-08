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

combineTool.py -M MultiDimFit -d ${ERA}_workspace.root -m 125 \
    --algo grid \
    --points $NUM --rMin $MIN --rMax $MAX \
    -n ${ERA}
python ${CMSSW_BASE}/bin/slc6_amd64_gcc530/plot1DScan.py \
    --main higgsCombine${ERA}.MultiDimFit.mH125.root \
    --POI $POI \
    --output ${ERA}_plot_nll_${POI} \
    --translate combine/translate.json
