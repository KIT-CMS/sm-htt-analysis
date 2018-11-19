#!/bin/bash

source utils/setup_cmssw.sh

ERA=$1
DATACARD=${ERA}_workspace.root
MASS=125
NUM_TOYS=50 # multiply x10

# Get test statistic value
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD

# Throw toys
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1230 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1231 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1232 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1233 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1234 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1235 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1236 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1237 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1238 -t $NUM_TOYS
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s 1239 -t $NUM_TOYS

# Collect results
combineTool.py -M CollectGoodnessOfFit --input \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1230.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1231.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1232.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1233.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1234.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1235.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1236.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1237.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1238.root \
    higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1239.root \
    --output gof.json

# Plot
plotGof.py --statistic saturated --mass $MASS.0 --output gof gof.json
