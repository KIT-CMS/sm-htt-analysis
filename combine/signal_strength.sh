#!/bin/bash
set -e
source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh

ERA=$1
STXS_FIT=$2
DATACARDDIR=$3
CHANNEL=$4
[[ -d $DATACARDDIR ]] || ( echo $DATACARDDIR is not a valid directory; exit 1 )
if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
    STXS_SIGNALS=stxs_stage0
elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
    STXS_SIGNALS=stxs_stage1p1
else # Hesse default
    STXS_SIGNALS=stxs_stage0
fi
WORKSPACE=$DATACARDDIR/${ERA}-${STXS_FIT}-workspace.root
[[ -z $5 ]] && LOGFILE="output/log/signal-strength-$ERA-$CHANNEL-$STXS_FIT.log" || LOGFILE="output/log/signal-strength-$ERA-$5-$CHANNEL-$STXS_FIT.log"
[[ -z $5 ]] && OUTPUTFILE="output/signalStrength/signal-strength-$CHANNEL-$STXS_FIT.txt" || OUTPUTFILE="output/signalStrength/signal-strength-$ERA-$5-$CHANNEL-$STXS_FIT.txt"
FITFILE=$DATACARDDIR/higgsCombine${ERA}-${STXS_FIT}.MultiDimFit.mH125.root
# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all ERAs
ulimit -s unlimited

if [ $STXS_FIT == "robustHesse" ]
then
    logandrun combine \
        -M MaxLikelihoodFit \
        -m 125 -d $WORKSPACE \
        --robustFit 1 -n $ERA -v1 \
        --robustHesse 1 \
        -t -1 --expectSignal 1 \
        --X-rtd MINIMIZER_analytic\
        --cminDefaultMinimizerStrategy 0 \
        | tee $LOGFILE
    #python combine/check_mlfit.py fitDiagnostics${ERA}.root
    root -l fitDiagnostics${ERA}.root <<< "fit_b->Print(); fit_s->Print()" \
    | grep "covariance matrix quality" | tee -a $LOGFILE | tee $OUTPUTFILE
fi
if [ $STXS_FIT == "inclusive" ] || [ $STXS_FIT == "stxs_stage0" ] || [ $STXS_FIT == "stxs_stage1p1" ]
then
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
    python combine/print_fitresult.py $FITFILE | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | tee $OUTPUTFILE
fi
