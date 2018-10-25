#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
VARIABLE=$2
CATEGORIES=$3
JETFAKES=$4
EMBEDDING=$5
CHANNELS=${@:6}







EMBEDDING_ARG=""
if [ $EMBEDDING == 1 ]
then
    EMBEDDING_ARG="--embedding"
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

mkdir -p plots
for FILE in "${ERA}_datacard_shapes_prefit.root"
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes.py -i $FILE -c $CHANNELS -e $ERA $OPTION --gof-variable $VARIABLE --categories gof $JETFAKES_ARG $EMBEDDING_ARG -l
    done
done
