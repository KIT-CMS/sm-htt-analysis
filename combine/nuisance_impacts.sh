#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --doInitialFit --robustFit 1 -t -1 --expectSignal=1 --parallel 20 --minimizerAlgoForMinos=Minuit2,Migrad
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --doFits --parallel 20 --robustFit 1 -t -1 --expectSignal=1 --minimizerAlgoForMinos=Minuit2,Migrad # --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP # with this options it does not seem to find an end
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --output ${ERA}_impacts.json
plotImpacts.py -i ${ERA}_impacts.json -o ${ERA}_impacts
