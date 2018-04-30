#!/bin/bash

source utils/setup_cmssw.sh

ERA=$1
DATACARD=${ERA}_datacard.txt
SEED=1234
MASS=125
NUM_TOYS=300

# Get test statistic value
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD

# Throw toys
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s $SEED -t $NUM_TOYS

# Collect results
combineTool.py -M CollectGoodnessOfFit --input higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.$SEED.root --output gof.json

# Plot
plotGof.py --statistic saturated --mass $MASS.0 --output gof gof.json
