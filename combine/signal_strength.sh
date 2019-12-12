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
    LOGFILE="output/log/hesse-$ERA-$TAG-$CHANNEL-$STXS_FIT.log"
    OUTPUTFILE="output/signalStrength/hesse-$ERA-$TAG-$CHANNEL-$STXS_FIT.txt"
else
    LOGFILE="output/log/signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT.log"
    OUTPUTFILE="output/signalStrength/signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT.txt"
fi
# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all ERAs
ulimit -s unlimited

if [[ $HESSE == "robustHesse" ]]
then
    logandrun combine \
        -M FitDiagnostics \
        -m 125 -d $WORKSPACE \
        --robustFit 1 -n $ERA -v1 \
        --robustHesse 1 \
        -t -1 --expectSignal 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        | tee $LOGFILE
    #python combine/check_mlfit.py fitDiagnostics${ERA}.root
    root -l fitDiagnostics${ERA}.root <<< "fit_b->Print(); fit_s->Print()" \
    | tee -a $LOGFILE | tee $OUTPUTFILE
else
    FITFILE=$DATACARDDIR/higgsCombine${ERA}-${STXS_FIT}.MultiDimFit.mH125.root
    logandrun combineTool.py \
        -M MultiDimFit\
        -m 125 -d $WORKSPACE \
        --algo singles \
        --robustFit 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        --floatOtherPOIs 1 \
        -t -1 --expectSignal 1 \
        -n $ERA -v1 \
        | tee $LOGFILE
    [[ ! -f higgsCombine${ERA}.MultiDimFit.mH125.root ]] || mv higgsCombine${ERA}.MultiDimFit.mH125.root $FITFILE
    logandrun python combine/print_fitresult.py $FITFILE | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | grep -E '^r' | tee $OUTPUTFILE
fi
