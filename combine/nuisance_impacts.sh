#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --doInitialFit --robustFit 1 \
    --setParameters taues=-0.5 \
    --setParameterRanges taues=-2.4,1.6 \
     --redefineSignalPOIs taues \
    --parallel 32
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    --doFits --parallel 20 --robustFit 1 \
     --redefineSignalPOIs taues \
    --setParameters taues=-0.5 \
    --setParameterRanges taues=-2.4,1.6 \
    --parallel 32
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --output ${ERA}_impacts.json --redefineSignalPOIs taues
plotImpacts.py -i ${ERA}_impacts.json -o ${ERA}_impacts
