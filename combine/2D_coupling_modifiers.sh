#!/bin/bash

source utils/setup_cmssw.sh

combineTool.py -M T2W -m 125 -o "workspace.root" -P HiggsAnalysis.CombinedLimit.HiggsCouplings:cVcF -i datacard.txt
#combineTool.py -M MultiDimFit --robustFit 1 -m 125 -d workspace.root --algo singles
combineTool.py -M MultiDimFit --robustFit 1 -m 125 -d workspace.root --algo grid --points 1600 --setPhysicsModelParameterRanges kappa_F=0.0,2.0:kappa_V=0.0,2.0 
python combine/plotMultiDimFit_couplings.py --title-right="35.9 fb^{-1} (13 TeV)" --cms-sub="Preliminary" --mass 125 -o 2D_limit_mH125 higgsCombine.Test.MultiDimFit.mH125.root
