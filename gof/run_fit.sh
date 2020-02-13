#!/bin/bash
set -e
source utils/bashFunctionCollection.sh
source utils/setup_cmssw.sh

ERA=$1

WORKSPACE=${ERA}_workspace.root
ID=$ERA

LOGFILE="output/log/$ID.log"
OUTPUTFILE="output/signalStrength/$ID.txt"
# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all ERAs
ulimit -s unlimited

logandrun combine \
    -M FitDiagnostics \
    -m 125 -d $WORKSPACE \
    --robustFit 1 -v1 \
    --robustHesse 1 \
    -n .$ID \
    --setParameters r=0 --freezeParameters r \
    --X-rtd MINIMIZER_analytic \
    --cminDefaultMinimizerStrategy 0 \
    | tee $LOGFILE
FITFILE=fitDiagnostics.${ID}.MultiDimFit.mH125.root
mv fitDiagnostics.${ID}.root $FITFILE
#python combine/check_mlfit.py fitDiagnostics${ERA}.root
logandrun root -l $FITFILE <<< "fit_b->Print(); fit_s->Print()" \
| tee -a $LOGFILE | tee $OUTPUTFILE

python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
    fitDiagnostics.${ID}.MultiDimFit.mH125.root -a  \
    -f html > nuisances.html
