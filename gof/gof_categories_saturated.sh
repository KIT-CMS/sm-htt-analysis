source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh
source utils/setup_python.sh

MODE=$1
TAG=$2
ERA=$3
CHANNEL=$4
CATEGORY=$5
MASK=$6
PLOT=$7

VARIABLE="NNOutput"
ALGO="saturated"
ID=${TAG}-${ERA}-${CHANNEL}-${VARIABLE}-${CATEGORY}
DATACARD=output/datacards/${ERA}-${TAG}-smhtt-ML/stxs_stage0/${CHANNEL}/125/${ERA}-inclusive-${CHANNEL}-workspace.root
if [[ $CHANNEL == *"cmb"* ]]; then
    DATACARD=output/datacards/${ERA}-${TAG}-smhtt-ML/stxs_stage0/${CHANNEL}/125/${ERA}-inclusive-workspace.root
fi
MASS=125
NUM_TOYS=50 # multiply x10

if [[ ! -d output/gof/${ID}/${ERA}_plots ]]
then
    mkdir -p output/gof/${ID}/${ERA}_plots
fi
   
echo "Doing ${ALGO} GoF for ${ID}..."
LOGFILE=output/gof/${ID}/testlog.log
echo "Running Saturated GoF for ${ID} with settings:" > $LOGFILE
echo "Mode:     ${MODE}" >> $LOGFILE
echo "Tag:      ${TAG}" >> $LOGFILE
echo "Era :     ${ERA}" >> $LOGFILE
echo "Channel:  ${CHANNEL}" >> $LOGFILE
echo "Category: ${CATEGORY}" >> $LOGFILE
echo "Mask:     ${MASK}" >> $LOGFILE
echo "Plot:     ${PLOT}" >> $LOGFILE
echo "Datacard: ${DATACARD}" >> $LOGFILE
# # Get test statistic value
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD --fixedSignalStrength=0 --setParameters $MASK >> $LOGFILE

# Throw toys
TOYSOPT="--toysFreq"

combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1230 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1231 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1232 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1233 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1234 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1235 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1236 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1237 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1238 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $DATACARD -s 1239 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters ${MASK} > /dev/null &
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
    --output output/gof/${ID}/gof_${ALGO}.json >> $LOGFILE

mv output/gof/${ID}/gof_${ALGO}.json output/gof/${ID}/gof.json

# Plot
plotGof.py --statistic $ALGO --mass $MASS.0 --output gof output/gof/${ID}/gof.json
    mv gof.p{df,ng} output/gof/${ID}/

## run fit 
# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all ERAs
ulimit -s unlimited

combine \
    -M FitDiagnostics \
    -m 125 -d $DATACARD \
    --robustFit 1 -v1 \
    --robustHesse 1 \
    -n .$ID \
    --setParameters r=0,${MASK} --freezeParameters r \
    --X-rtd MINIMIZER_analytic \
    --cminDefaultMinimizerStrategy 0 \
    >> $LOGFILE 
FITFILE=output/gof/${ID}/fitDiagnostics.${ID}.MultiDimFit.mH125.root
mv fitDiagnostics.${ID}.root $FITFILE
#python combine/check_mlfit.py fitDiagnostics${ERA}.root
# root -b -l $FITFILE <<< "fit_b->Print(); fit_s->Print()" >> $LOGFILE

python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
    $FITFILE -a  \
    -f html > output/gof/${ID}/nuisances.html

# Prefit shapes
if [[ "$PLOT" == "1" ]]; then
    echo "Plotting Prefit/Postfit for $ID..."
    PostFitShapesFromWorkspace -m 125 -w $DATACARD \
        -d output/datacards/${ERA}-${TAG}-smhtt-ML/stxs_stage0/${CHANNEL}/125/combined.txt.cmb -o output/gof/${ID}/datacard-shapes-prefit.root >> $LOGFILE

    PostFitShapesFromWorkspace -m 125 -w $DATACARD \
        -d output/datacards/${ERA}-${TAG}-smhtt-ML/stxs_stage0/${CHANNEL}/125/combined.txt.cmb -o output/gof/${ID}/datacard-shapes-postfit-b.root \
        -f $FITFILE:fit_b --postfit --sampling --skip-prefit >> $LOGFILE
    ## Plot the prefit and the postfit shape
        
    if [[ $CATEGORY != *"999"* ]]; then    
        PLOTDIR=output/gof/${ID}
        ./plotting/plot_shapes.py -i output/gof/${ID}/datacard-shapes-prefit.root -o $PLOTDIR \
            -c ${CHANNEL} -e $ERA --categories $CATEGORIES \
            --fake-factor --embedding --normalize-by-bin-width \
            -l --train-ff True --train-emb True --blinded-shapes --single-category ${CATEGORY} >> $LOGFILE

        ./plotting/plot_shapes.py -i output/gof/${ID}/datacard-shapes-postfit-b.root -o $PLOTDIR \
            -c ${CHANNEL} -e $ERA --categories $CATEGORIES \
            --fake-factor --embedding --normalize-by-bin-width \
            -l --train-ff True --train-emb True --blinded-shapes --single-category ${CATEGORY} >> $LOGFILE
    elif [[ $CATEGORY == *"999"* ]]; then
        source gof/build_mask.sh
        PLOTDIR=output/gof/${ID}
        backlist=$(buildCategories 2 $TAG $ERA $CHANNEL "backgrounds")
        for plotcat in "${backlist[@]}"; do
            ./plotting/plot_shapes.py -i output/gof/${ID}/datacard-shapes-prefit.root -o $PLOTDIR \
                -c ${CHANNEL} -e $ERA --categories $CATEGORIES \
                --fake-factor --embedding --normalize-by-bin-width \
                -l --train-ff True --train-emb True --blinded-shapes --single-category ${plotcat} >> $LOGFILE

            ./plotting/plot_shapes.py -i output/gof/${ID}/datacard-shapes-postfit-b.root -o $PLOTDIR \
                -c ${CHANNEL} -e $ERA --categories $CATEGORIES \
                --fake-factor --embedding --normalize-by-bin-width \
                -l --train-ff True --train-emb True --blinded-shapes --single-category ${plotcat} >> $LOGFILE
        done
    fi
else
    echo "Generating no plots.."
fi
rm higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root 
rm higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.*.root
rm higgsCombine.${ID}.FitDiagnostics.mH$MASS.root