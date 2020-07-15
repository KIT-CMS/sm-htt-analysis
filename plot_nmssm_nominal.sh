ERA=$1
CHANNEL=$2
VARIABLE=$3
MODE=$4


if [ "$MODE" == "prefit" ]; then
python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  -c $CHANNEL --emb   --output-dir plots/prefit/blinded/ --ff --prefit --shapes CMSSW_10_2_16_UL/src/output_${ERA}_${CHANNEL}_nmssm_500_100/${ERA}/cmb/prefitshape.root 
else

./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE
python plot_nmssm_nominal.py  -v ${VARIABLE} --era Run${ERA}  --shapes output/shapes/${ERA}_${CHANNEL}_${VARIABLE}/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}-${CHANNEL}-shapes.root -c $CHANNEL --emb   --output-dir plots/unblinded/nolog --ff 

fi

wait




