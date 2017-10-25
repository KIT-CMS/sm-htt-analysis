#!/bin/bash

source utils/setup_cmssw.sh

text2workspace.py -m 125 datacard.txt -o workspace.root
combineTool.py -M Impacts -m 125 -d workspace.root --doInitialFit
combineTool.py -M Impacts -m 125 -d workspace.root --doFits --parallel 20
combineTool.py -M Impacts -m 125 -d workspace.root --output impacts.json
plotImpacts.py -i impacts.json -o impacts
