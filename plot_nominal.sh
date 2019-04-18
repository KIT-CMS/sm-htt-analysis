ERA=$1
CHANNEL=$2
VARIABLE=$3

./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE 

python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb --comparison &
python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL --emb  &
python plot_nominal.py  -v $VARIABLE --era Run${ERA}  --shapes ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root -c $CHANNEL  &
wait

