#!/bin/bash

source utils/setup_cmssw.sh

ERA=$1
DATACARD=${ERA}_workspace.root
MASS=125
NUM_TOYS=50 # multiply x10

if [[ ! -d ${ERA}_plots ]]
then
    mkdir -p ${ERA}_plots
fi

for ALGO in "saturated" "KS" "AD"
do
    # Get test statistic value
    if [[ "$ALGO" == "saturated" ]]
    then
        combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD --fixedSignalStrength=0
    else
        combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD --plots --fixedSignalStrength=0
    fi

    # Throw toys
    TOYSOPT=""
    if [[ "$ALGO" == "saturated" ]]
    then
        TOYSOPT="--toysFreq"
    fi

    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1230 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1231 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1232 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1233 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1234 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1235 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1236 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1237 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1238 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit --algo=$ALGO -m $MASS -d $DATACARD -s 1239 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0

    # Collect results
    combineTool.py -M CollectGoodnessOfFit --input \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1230.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1231.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1232.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1233.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1234.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1235.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1236.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1237.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1238.root \
        higgsCombineTest.GoodnessOfFit.mH$MASS.root higgsCombineTest.GoodnessOfFit.mH$MASS.1239.root \
        --output gof_${ALGO}.json

    if [[ "$ALGO" == "saturated" ]]
    then
        mv gof_${ALGO}.json gof.json
    fi

    # Plot
    if [[ "$ALGO" != "saturated" ]]
    then
        plotGof.py --statistic $ALGO --mass $MASS.0 --output gof_${ALGO} gof_${ALGO}.json
        ./gof/plot_gof_metrics.py -e $ERA -g $ALGO
    else
        plotGof.py --statistic $ALGO --mass $MASS.0 --output gof gof.json
    fi
done
