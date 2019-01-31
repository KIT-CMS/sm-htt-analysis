#!/bin/bash

source utils/setup_cmssw.sh

ERA=$1
MASS=125
TOYS=30

STATISTIC=saturated

# Get test statistic value
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0

# Throw toys
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1230 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1231 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1232 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1233 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1234 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1235 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1236 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1237 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1238 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &
combine -M GoodnessOfFit --algo=${STATISTIC} -m $MASS -d ${ERA}_workspace.root \
        -n ${ERA} \
        -s 1239 -t $TOYS \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 &

wait

# Collect results
combineTool.py -M CollectGoodnessOfFit \
    --input higgsCombine${ERA}.GoodnessOfFit.mH$MASS.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1230.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1231.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1232.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1233.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1234.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1235.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1236.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1237.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1238.root \
        higgsCombine${ERA}.GoodnessOfFit.mH$MASS.1239.root \
    --output gof.json

# Plot
plotGof.py --statistic ${STATISTIC} --mass $MASS.0 --output gof gof.json
