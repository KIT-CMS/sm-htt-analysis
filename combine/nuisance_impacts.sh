#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

text2workspace.py -m 125 ${ERA}_datacard.txt -o ${ERA}_workspace.root
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --doInitialFit
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --doFits --parallel 20
combineTool.py -M Impacts -m 125 -d ${ERA}_workspace.root --output ${ERA}_impacts.json
plotImpacts.py -i ${ERA}_impacts.json -o ${ERA}_impacts
