#!/bin/bash
set -e
source utils/bashFunctionCollection.sh
source utils/setup_cmssw.sh

ERA=$1
STXS_FIT=$2
DATACARDDIR=$3
CHANNEL=$4
TAG=$5
HESSE=$6
[[ -d $DATACARDDIR ]] || ( echo $DATACARDDIR is not a valid directory; exit 1 )
if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
    STXS_SIGNALS=stxs_stage0
elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
    STXS_SIGNALS=stxs_stage1p1
fi
WORKSPACE=$DATACARDDIR/${ERA}-${STXS_FIT}-workspace.root
if [[ $HESSE == "robustHesse" ]];then
    ID=hesse-$ERA-$TAG-$CHANNEL-$STXS_FIT
elif [[ $HESSE == "bkg_robustHesse" ]];then
    ID=hesse-$ERA-$TAG-$CHANNEL-$STXS_FIT
    WORKSPACE=$DATACARDDIR/${ERA}-inclusive-workspace.root
else
    ID=signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT
fi
LOGFILE="output/log/$ID.log"
OUTPUTFILE="output/signalStrength/$ID.txt"
# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all ERAs
ulimit -s unlimited

if [[ $HESSE == "robustHesse" ]]
then
    logandrun combine \
        -n .$ID \
        -M FitDiagnostics \
        -m 125 -d $WORKSPACE \
        --robustFit 1 -v1 \
        --robustHesse 1 \
        -t -1 --expectSignal 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        | tee $LOGFILE
    FITFILE=$DATACARDDIR/fitDiagnostics.${ID}.MultiDimFit.mH125.root
    mv fitDiagnostics.${ID}.root $FITFILE
    python combine/check_mlfit.py fitDiagnostics${ERA}.root
    logandrun root -l -b $FITFILE <<< "fit_b->Print(); fit_s->Print()" \
    | tee -a $LOGFILE | tee $OUTPUTFILE
elif [[ $HESSE == "bkg_robustHesse" ]]
then
    logandrun combine \
        -n .$ID \
        -M FitDiagnostics \
        -m 125 -d $WORKSPACE \
        --robustFit 1 -v1 \
        --robustHesse 1 \
        --setParameters r=0 --freezeParameters r \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        | tee $LOGFILE
    FITFILE=$DATACARDDIR/fitDiagnostics.${ID}.MultiDimFit.mH125.root
    mv fitDiagnostics.${ID}.root $FITFILE
    python combine/check_mlfit.py fitDiagnostics.${ID}.root
    logandrun root -l -b $FITFILE <<< "fit_b->Print(); fit_s->Print()" \
    | tee -a $LOGFILE | tee $OUTPUTFILE
else
    FITFILE=$DATACARDDIR/higgsCombine.${ID}.MultiDimFit.mH125.root
    logandrun combineTool.py \
        -n .$ID \
        -M MultiDimFit\
        -m 125 -d $WORKSPACE \
        --algo singles \
        --robustFit 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        --floatOtherPOIs 1 \
        -t -1 --expectSignal 1 \
        -v1 \
        | tee $LOGFILE
    mv higgsCombine.${ID}.MultiDimFit.mH125.root $FITFILE
    logandrun python combine/print_fitresult.py $FITFILE | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | grep -E '^r' | tee $OUTPUTFILE
fi
