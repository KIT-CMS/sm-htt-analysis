#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --doInitialFit --robustFit 1 \
    -t -1 --expectSignal=1 \
    --parallel 32
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --doFits --parallel 20 --robustFit 1 \
    -t -1 --expectSignal=1 \
    --parallel 32
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --output ${ERA}_impacts.json
plotImpacts.py -i ${ERA}_impacts.json -o ${ERA}_impacts
