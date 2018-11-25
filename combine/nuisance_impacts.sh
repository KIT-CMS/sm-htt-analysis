#!/bin/bash

ERAS=$1

TAG=""
for ERA in ${ERAS}
do
    TAG="${TAG}${ERA}_"
done

source utils/setup_cmssw.sh

combineTool.py -M Impacts -m 125 -d ${TAG}workspace.root --doInitialFit --robustFit 1 -t -1 --expectSignal=1 --parallel 20 --minimizerAlgoForMinos=Minuit2,Migrad
combineTool.py -M Impacts -m 125 -d ${TAG}workspace.root --doFits --parallel 20 --robustFit 1 -t -1 --expectSignal=1 --minimizerAlgoForMinos=Minuit2,Migrad # --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP # with this options it does not seem to find an end
combineTool.py -M Impacts -m 125 -d ${TAG}workspace.root --output ${TAG}impacts.json
plotImpacts.py -i ${TAG}impacts.json -o ${TAG}impacts
