source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
CHANNEL=$2
VARIABLE=$3

./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNEL $VARIABLE

plotting/plot_shapes_control.py -l  --era Run${ERA} --input ${ERA}_${CHANNEL}_${VARIABLE}_shapes.root --variables $VARIABLE --channels $CHANNEL --embedding --fake-factor


