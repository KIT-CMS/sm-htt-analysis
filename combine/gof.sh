#!/bin/bash

source utils/setup_cmssw.sh

DATACARD=datacard.txt
SEED=1234
MASS=125

# Get test statistic value
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD

# Throw toys
combine -M GoodnessOfFit --algo=saturated -m $MASS -d $DATACARD -s $SEED -t 100

# Collect results
combineTool.py -M CollectGoodnessOfFit --input higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.$SEED.root --output gof.json

# Plot
plotGof.py --statistic saturated --mass $MASS.0 --output gof gof.json
