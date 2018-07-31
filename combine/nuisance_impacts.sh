#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --doInitialFit --robustFit 1 -t -1 --expectSignal=1 --parallel 20
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --doFits --parallel 20 --robustFit 1 -t -1 --expectSignal=1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --output ${ERA}_impacts.json
plotImpacts.py -i ${ERA}_impacts.json -o ${ERA}_impacts
