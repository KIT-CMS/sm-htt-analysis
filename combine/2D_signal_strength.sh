#!/bin/bash

source utils/setup_cmssw.sh

combineTool.py -M T2W -m 125 -o "workspace.root" -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO '"map=^.*/ggH.?$:r_ggH[0,0,200]"' --PO '"map=^.*/qqH$:r_qqH[0,0,200]"' -i datacard.txt
combineTool.py -M MultiDimFit -m 125 -d workspace.root --algo singles #-t -1 --setPhysicsModelParameters r_ggH=2.0,r_qqH=0.0
#combineTool.py -M MultiDimFit -m 125 -d workspace.root --algo grid --points 400 --setPhysicsModelParameterRanges r_ggH=0.0,3.0:r_qqH=0.0,3.0 
#python combine/plotMultiDimFit.py --title-right="35.9 fb^{-1} (13 TeV)" --cms-sub="Preliminary" --mass 125 -o 2D_limit_mH125 higgsCombine.Test.MultiDimFit.mH125.root
