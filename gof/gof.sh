#!/bin/bash

source utils/setup_cmssw.sh

ERA=$1
CHANNEL=$2
VARIABLE=$3

ID=${ERA}-${CHANNEL}-${VARIABLE}
DATACARD=output/datacards/${ID}-smhtt-gof/${ID}-workspace.root
MASS=125
NUM_TOYS=50 # multiply x10

if [[ ! -d output/gof/${ID}/${ERA}_plots ]]
then
    mkdir -p output/gof/${ID}/${ERA}_plots
fi

for ALGO in "saturated" "KS" "AD"
do
    # Get test statistic value
    if [[ "$ALGO" == "saturated" ]]
    then
        combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD --fixedSignalStrength=0
    else
        combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD --plots --fixedSignalStrength=0
    fi

    # Throw toys
    TOYSOPT=""
    if [[ "$ALGO" == "saturated" ]]
    then
        TOYSOPT="--toysFreq"
    fi

    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1230 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1231 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1232 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1233 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1234 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1235 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1236 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1237 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1238 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0
    combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1239 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0

    # Collect results
    combineTool.py -M CollectGoodnessOfFit --input \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1230.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1231.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1232.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1233.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1234.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1235.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1236.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1237.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1238.root \
        higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1239.root \
        --output output/gof/${ID}/gof_${ALGO}.json

    mv higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.123?.root output/datacards/${ID}/
    if [[ "$ALGO" == "saturated" ]]
    then
        mv output/gof/${ID}/gof_${ALGO}.json output/gof/${ID}/gof.json
    fi

    # Plot
    if [[ "$ALGO" != "saturated" ]]
    then
        plotGof.py --statistic $ALGO --mass $MASS.0 --output gof_${ALGO} output/gof/${ID}/gof_${ALGO}.json
        mv htt_${CHANNEL}_300_${ERA}gof_${ALGO}.p{df,ng} output/gof/${ID}/
        ./gof/plot_gof_metrics.py -e $ERA -g $ALGO -o output/gof/${ID}/${ERA}_plots -i output/datacards/${ID}/higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root
    else
        plotGof.py --statistic $ALGO --mass $MASS.0 --output output/gof/${ID}/gof output/gof/${ID}/gof.json
    fi
done
