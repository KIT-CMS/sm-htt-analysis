#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

#FIXED=1.0 # for compatibility with SM expectation
FIXED=0.75 # forcompatibility with inclusive bestfit signal strength
combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace.root \
    --algo fixed --robustFit 1 \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --fixedPointPOIs r_qqH_REST=${FIXED},r_ggH_GE2J=${FIXED},r_VBFTOPO=${FIXED},r_qqH_VH2JET=${FIXED},r_ggH_1J_PTH_GT120=${FIXED},r_ggH_1J_PTH_0_60=${FIXED},r_qqH_PTJET1_GT200=${FIXED},r_ggH_1J_PTH_60_120=${FIXED},r_ggH_0J=${FIXED} \
    -n $ERA -v1

python combine/print_stage1_compatibility.py higgsCombine${ERA}.MultiDimFit.mH125.root
