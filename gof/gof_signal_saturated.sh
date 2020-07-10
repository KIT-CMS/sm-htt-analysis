#!/usr/bin/env bash
source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh
source utils/setup_python.sh
source gof/build_mask_signal.sh

MODE=$1
TAG=$2
ERA=$3
CHANNEL=$4
CATEGORY=$5
MASK=$6
TAGTYPE=$7
PLOT=$8

VARIABLE="NNOutput"
ALGO="saturated"
ID=${TAG}-${ERA}-${CHANNEL}-${VARIABLE}-${CATEGORY}
DATACARD=output/datacards/${ERA}-${TAG}-smhtt-ML/${TAGTYPE}/${CHANNEL}/125/${ERA}-${TAGTYPE}-workspace.root
if [[ $CHANNEL == *"cmb"* ]]; then
    DATACARD=output/datacards/${ERA}-${TAG}-smhtt-ML/${TAGTYPE}/${CHANNEL}/125/${ERA}-${TAGTYPE}-workspace.root
fi
MASS=125
NUM_TOYS=50 # multiply x10

if [[ ! -d output/gof_signal/${ID}/${ERA}_plots ]]
then
    mkdir -p output/gof_signal/${ID}/${ERA}_plots
fi
# prepare plotting options for later
bkpIFS="$IFS"
IFS=","
backlist=$(buildCategories "14node" $TAG $ERA $CHANNEL "backgrounds")
IFS="$bkpIFS"
backlist=($backlist)
# IFS="," read -a plotlist < <(buildCategories 14node $TAG $ERA $CHANNEL backgrounds)
PLOTDIR=output/gof_signal/${ID}


echo "Doing ${ALGO} GoF for ${ID}..."
LOGFILE=output/gof_signal/${ID}/testlog.log
echo "Running Saturated GoF for ${ID} with settings:" > $LOGFILE
echo "Mode:     ${MODE}" >> $LOGFILE
echo "Tag:      ${TAG}" >> $LOGFILE
echo "Era :     ${ERA}" >> $LOGFILE
echo "Channel:  ${CHANNEL}" >> $LOGFILE
echo "Category: ${CATEGORY}" >> $LOGFILE
echo "Mask:     ${MASK}" >> $LOGFILE
echo "Plot:     ${PLOT}" >> $LOGFILE
echo "Datacard: ${DATACARD}" >> $LOGFILE
echo "Plotlist: ${backlist[@]}" >> $LOGFILE
# # Get test statistic value
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD --setParameters $MASK >> $LOGFILE

# Throw toys
TOYSOPT="--toysFreq"

combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1230 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1231 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1232 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1233 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1234 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1235 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1236 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1237 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1238 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1239 -t $NUM_TOYS $TOYSOPT --setParameters ${MASK} > /dev/null &
wait

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
    --output output/gof_signal/${ID}/gof_${ALGO}.json >> $LOGFILE

mv output/gof_signal/${ID}/gof_${ALGO}.json output/gof_signal/${ID}/gof.json

# Plot
plotGof.py --statistic $ALGO --mass $MASS.0 --output gof output/gof_signal/${ID}/gof.json
    mv gof.p{df,ng} output/gof_signal/${ID}/

rm higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root 
rm higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.*.root
rm higgsCombine.${ID}.FitDiagnostics.mH$MASS.root