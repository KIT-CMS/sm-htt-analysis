#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace.root \
    --algo fixed --robustFit 1 \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --fixedPointPOIs r_qqH_REST=-1.0618,r_ggH_GE2J=0.4676,r_VBFTOPO=0.9982,r_qqH_VH2JET=-1.1692,r_ggH_1J_PTH_GT120=1.8007,r_ggH_1J_PTH_0_60=-0.3422,r_qqH_PTJET1_GT200=1.4062,r_ggH_1J_PTH_60_120=1.2626,r_ggH_0J=-0.3977 \
    -n $ERA -v1

python combine/print_stage1_compatibility.py higgsCombine${ERA}.MultiDimFit.mH125.root
