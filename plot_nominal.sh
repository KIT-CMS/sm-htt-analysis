ERA=$1
CHANNEL=$2
VARIABLE=$3

./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE 

python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes output/shapes/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}--shapes.root -c $CHANNEL --emb --ff &
python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes output/shapes/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}--shapes.root -c $CHANNEL --emb  &
python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes output/shapes/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}--shapes.root -c $CHANNEL --ff  &
python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes output/shapes/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}--shapes.root -c $CHANNEL  &

wait

