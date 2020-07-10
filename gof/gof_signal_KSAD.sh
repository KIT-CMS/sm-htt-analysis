source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh
source utils/setup_python.sh

MODE=$1
TAG=$2
ERA=$3
CHANNEL=$4
CATEGORY=$5
TAGTYPE=$6
ALGO=$7
VARIABLE="NNOutput"
ID=${TAG}-${ERA}-${CHANNEL}-${VARIABLE}-${CATEGORY}
DATACARD=output/datacards/${ERA}-${TAG}-smhtt-ML/${TAGTYPE}/${CHANNEL}/125/${ERA}-${TAGTYPE}-workspace.root
MASS=125
NUM_TOYS=50 # multiply x10

if [[ ! -d output/gof_signal/${ID}/${ERA}_plots ]]
then
    mkdir -p output/gof_signal/${ID}/${ERA}_plots
fi

LOGFILE=output/gof${ID}/testlog_${ALGO}.log
echo "Doing ${ALGO} GoF for ${ID}..."
# Get test statistic value
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD --plots > /dev/null

# Throw toys
TOYSOPT=""

combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1230 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1231 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1232 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1233 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1234 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1235 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1236 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1237 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1238 -t $NUM_TOYS $TOYSOPT > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1239 -t $NUM_TOYS $TOYSOPT > /dev/null &
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
    --output output/gof_signal/${ID}/gof_${ALGO}.json > /dev/null
# Plot
plotGof.py --statistic $ALGO --mass $MASS.0 --output gof_${ALGO} output/gof_signal/${ID}/gof_${ALGO}.json
mv htt_${CHANNEL}*${ERA}gof_${ALGO}.p{df,ng} output/gof_signal/${ID}/
./gof/plot_gof_metrics.py -e $ERA -g $ALGO -o output/gof_signal/${ID}/${ERA}_plots -i higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root
