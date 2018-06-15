#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# 2D best-fit
MAKE_BESTFIT=1
if [ -n "$MAKE_BESTFIT" ]; then
    combineTool.py -M T2W -m 125 -o ${ERA}_workspace.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO '"map=^.*/ggH125.?$:r_ggH[0,0,200]"' --PO '"map=^.*/qqH125$:r_qqH[0,0,200]"' -i ${ERA}_datacard.txt
    combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace.root --algo singles --robustFit 1 -n $ERA
fi

# 2D plot with 400 fitted points
#MAKE_PLOT=1
if [ -n "$MAKE_PLOT" ]; then
    combineTool.py -M MultiDimFit -m 125 -d ${ERA}_workspace.root --algo grid --robustFit 1 --points 400 --setPhysicsModelParameterRanges r_ggH=0.0,3.0:r_qqH=0.0,3.0 -n $ERA
    python combine/plotMultiDimFit.py --title-right="35.9 fb^{-1} (13 TeV)" --cms-sub="Preliminary" --mass 125 -o 2D_limit_mH125 higgsCombine${ERA}.Test.MultiDimFit.mH125.root
fi
