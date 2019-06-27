#!/bin/bash

ERA=$1
source utils/setup_cmssw.sh

#combine -M MaxLikelihoodFit --robustFit 1 -m 125 -d ${ERA}_workspace.root

combineTool.py -M FitDiagnostics -m 125 -d "${ERA}"_workspace.root --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 -n ${ERA}
